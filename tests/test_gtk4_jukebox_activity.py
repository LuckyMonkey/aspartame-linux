import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "packages/gtk4-jukebox-activity"
sys.path.insert(0, str(PACKAGE))
from jukebox_playlist import Playlist, is_media, parse_m3u, write_m3u  # noqa: E402

# Written by GTK3 Jukebox (playlist.py write_playlist_to_file).
GTK3_PLAYLIST = "#EXTINF:Morning song\njournal://1111\n#EXTINF:Cat video\njournal://2222\n"


class FakeJournal:
    def __init__(self):
        self.saved = []

    def media(self):
        return [("1111", "Morning song", "audio/ogg"), ("2222", "Cat video", "video/webm")]

    def save_playlist(self, entry, title, text, bundle_id):
        self.saved.append((title, text, bundle_id))
        return entry or object()


def activity(metadata=None):
    from gtk4_activity_harness import load
    jukebox = load("gtk4-jukebox-activity", "jukeboxactivity4", "JukeboxActivity")
    jukebox.journal = FakeJournal()
    if metadata is not None:
        jukebox.metadata = metadata
    return jukebox


def test_gtk3_playlists_round_trip():
    tracks = parse_m3u(GTK3_PLAYLIST)
    assert tracks == [{"title": "Morning song", "path": "journal://1111"},
                      {"title": "Cat video", "path": "journal://2222"}]
    assert write_m3u(tracks) == GTK3_PLAYLIST
    assert parse_m3u("#EXTM3U\n#EXTINF:123,Song\n/media/song.ogg\n")[0]["title"] == "Song"


@pytest.mark.parametrize("text", ["not a playlist", "#EXTINF:x\nsong.ogg\n"])
def test_text_that_is_not_a_playlist_raises(text):
    with pytest.raises(ValueError):
        parse_m3u(text)


def test_playlist_order_and_navigation():
    playlist = Playlist(parse_m3u(GTK3_PLAYLIST))
    playlist.add("Third", "journal://3333")
    assert playlist.move(2, -1) == 1 and playlist.tracks[1]["title"] == "Third"
    assert playlist.step(1) and playlist.track["title"] == "Third"
    playlist.remove(0)
    assert playlist.track["title"] == "Third"
    assert playlist.step(1) and not playlist.step(1)


def test_media_types_follow_the_reference():
    assert is_media("audio/ogg") and is_media("video/mp4") and is_media("application/ogg")
    assert not is_media("text/plain") and not is_media(None)


def test_journal_media_are_added_from_the_picker(tmp_path):
    jukebox = activity()
    jukebox._show_picker(None)
    rows = (jukebox.picker_list.get_row_at_index(i) for i in range(2))
    names = [row.get_child().get_label() for row in rows]
    assert names == ["Morning song (audio)", "Cat video (video)"]
    jukebox._pick(None, "2222", "Cat video")
    path = tmp_path / "playlist"
    jukebox.write_file(path)
    assert path.read_text() == "#EXTINF:Cat video\njournal://2222\n"
    assert jukebox.metadata["mime_type"] == "audio/x-mpegurl"


def test_gtk3_playlist_object_opens(tmp_path):
    path = tmp_path / "playlist"
    path.write_text(GTK3_PLAYLIST)
    jukebox = activity({"mime_type": "audio/x-mpegurl"})
    jukebox.read_file(path)
    assert [t["title"] for t in jukebox.playlist.tracks] == ["Morning song", "Cat video"]


def test_opened_from_a_song_it_never_overwrites_the_song(tmp_path, monkeypatch):
    song = tmp_path / "song"
    song.write_bytes(b"OggS fake audio")
    jukebox = activity({"mime_type": "audio/ogg", "title": "Morning song"})
    monkeypatch.setattr(jukebox, "_object_id", lambda: "1111")
    jukebox.read_file(song)
    assert jukebox.playlist.tracks == [{"title": "Morning song", "path": "journal://1111"}]
    with pytest.raises(NotImplementedError):
        jukebox.write_file(tmp_path / "out")
    assert not (tmp_path / "out").exists() and jukebox.journal.saved == []
    jukebox._pick(None, "2222", "Cat video")
    with pytest.raises(NotImplementedError):
        jukebox.write_file(tmp_path / "out")
    assert jukebox.journal.saved == [("Morning song playlist", GTK3_PLAYLIST,
                                      "org.laptop.sugar.Jukebox")]
    assert song.read_bytes() == b"OggS fake audio"


def test_gtk4_jukebox_1_payload_keeps_only_real_files(tmp_path):
    path = tmp_path / "old.json"
    path.write_text('{"selected": 0, "tracks": [["Morning Bell", "Demo track"],'
                    ' ["a.ogg", "Local file", "file:///home/a.ogg"]]}')
    jukebox = activity({"mime_type": ""})
    jukebox.read_file(path)
    assert jukebox.playlist.tracks == [{"title": "a.ogg", "path": "file:///home/a.ogg"}]


def test_corrupt_playlist_raises(tmp_path):
    path = tmp_path / "bad"
    path.write_bytes(b"\xff\xfe not a valid payload")
    with pytest.raises(ValueError):
        activity({"mime_type": "audio/x-mpegurl"}).read_file(path)


def test_bundle_is_registered():
    info = (PACKAGE / "activity/activity.info").read_text()
    assert "org.laptop.sugar.Jukebox" in info
    assert "sugar-activity4 jukeboxactivity4.JukeboxActivity" in info
    assert "mime_types" in info and "audio/x-mpegurl" in info and "video/mp4" in info
