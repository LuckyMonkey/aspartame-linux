"""Jukebox playlists, independent of GTK.

A playlist is the GTK3 Jukebox format (sugarlabs/jukebox-activity,
playlist.py): an extended M3U file with ``#EXTINF:<title>`` before each
track. A track path is ``journal://<object id>`` for a Journal entry, or a
URI or absolute path for a local file.
"""

M3U_MIME = "audio/x-mpegurl"
MEDIA_PREFIXES = ("audio/", "video/")
MEDIA_EXTRA = {"application/ogg", "application/x-ogm-video", "application/x-ogm-audio"}


def is_media(mime_type):
    mime_type = (mime_type or "").split(";")[0].strip()
    return mime_type.startswith(MEDIA_PREFIXES) or mime_type in MEDIA_EXTRA


def is_playlist(mime_type):
    return (mime_type or "") in (M3U_MIME, "audio/mpegurl")


def journal_path(object_id):
    return "journal://" + object_id


def journal_id(path):
    return path[len("journal://"):] if path.startswith("journal://") else None


def _valid_path(path):
    return path.startswith(("journal://", "file://", "http://", "https://", "/"))


def parse_m3u(text):
    """Return ``[{"title", "path"}]``; anything that is not a playlist raises."""
    tracks, title = [], None
    for number, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line or line == "#EXTM3U":
            continue
        if line.startswith("#EXTINF:"):
            # GTK3 writes the bare title; standard M3U writes "<seconds>,<title>".
            info = line[len("#EXTINF:"):]
            head, comma, rest = info.partition(",")
            title = rest if comma and head.strip().lstrip("-").isdigit() else info
            continue
        if line.startswith("#"):
            continue
        if not _valid_path(line):
            raise ValueError("line %d is not a track: %r" % (number, line[:40]))
        tracks.append({"title": (title or line.rsplit("/", 1)[-1]).strip(), "path": line})
        title = None
    return tracks


def write_m3u(tracks):
    return "".join("#EXTINF:%s\n%s\n" % (t["title"].replace("\n", " "), t["path"]) for t in tracks)


def from_legacy_json(payload):
    """GTK4 Jukebox 1 saved ``{"tracks": [[name, detail, uri?]], "selected"}``."""
    tracks = payload.get("tracks")
    if not isinstance(tracks, list):
        raise ValueError("tracks must be a list")
    # Its demo tracks had no media behind them; only real files carry over.
    return [{"title": str(t[0]), "path": str(t[2])} for t in tracks
            if isinstance(t, list) and len(t) > 2 and t[2] and _valid_path(str(t[2]))]


class Playlist:
    def __init__(self, tracks=None):
        self.tracks = list(tracks or [])
        self.current = 0 if self.tracks else -1

    def __len__(self):
        return len(self.tracks)

    def add(self, title, path):
        self.tracks.append({"title": title, "path": path})
        if self.current < 0:
            self.current = 0
        return len(self.tracks) - 1

    def remove(self, index):
        del self.tracks[index]
        if index < self.current or self.current >= len(self.tracks):
            self.current -= 1
        if self.tracks and self.current < 0:
            self.current = 0

    def move(self, index, step):
        other = index + step
        if not (0 <= index < len(self.tracks) and 0 <= other < len(self.tracks)):
            return index
        self.tracks[index], self.tracks[other] = self.tracks[other], self.tracks[index]
        if self.current in (index, other):
            self.current = other if self.current == index else index
        return other

    def step(self, direction):
        """Move to the previous/next track; False at either end."""
        target = self.current + direction
        if not 0 <= target < len(self.tracks):
            return False
        self.current = target
        return True

    @property
    def track(self):
        return self.tracks[self.current] if 0 <= self.current < len(self.tracks) else None
