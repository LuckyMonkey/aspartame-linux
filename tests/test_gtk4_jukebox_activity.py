import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "packages/gtk4-jukebox-activity"
sys.path.insert(0, str(PACKAGE))
from jukebox_playlist import Playlist, is_media, parse_m3u, write_m3u  # noqa: E402
from gtk4_activity_harness import needs_gtk4, run  # noqa: E402

# Written by GTK3 Jukebox (playlist.py write_playlist_to_file).
GTK3_PLAYLIST = "#EXTINF:Morning song\njournal://1111\n#EXTINF:Cat video\njournal://2222\n"


SETUP = """
from jukeboxactivity4 import JukeboxActivity


class FakeJournal:
    def __init__(self):
        self.saved = []

    def media(self):
        return [("1111", "Morning song", "audio/ogg"), ("2222", "Cat video", "video/webm")]

    def save_playlist(self, entry, title, text, bundle_id):
        self.saved.append((title, text, bundle_id))
        return entry or object()


def jukebox(metadata=None):
    activity = JukeboxActivity(None, journal=FakeJournal())
    if metadata is not None:
        activity.metadata = metadata
    return activity
"""


def run_jukebox(body):
    return run("gtk4-jukebox-activity", SETUP + body)


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


@needs_gtk4
def test_journal_media_are_added_from_the_picker(tmp_path):
    out = run_jukebox(f"""
activity = jukebox()
activity._show_picker(None)
print("picker", [activity.picker_list.get_row_at_index(i).get_child().get_text() for i in range(2)])
activity._pick(None, "2222", "Cat video")
activity._pick(None, "1111", "Morning song")
print("current", activity.playlist.track["title"])
activity.write_file({str(tmp_path / 'playlist')!r})
print("mime", activity.metadata["mime_type"])
""")
    assert "picker ['Morning song (audio)', 'Cat video (video)']" in out
    assert "current Cat video" in out   # adding never changes the current track
    assert (tmp_path / "playlist").read_text() == \
        "#EXTINF:Cat video\njournal://2222\n#EXTINF:Morning song\njournal://1111\n"
    assert "mime audio/x-mpegurl" in out


@needs_gtk4
def test_gtk3_playlist_object_opens(tmp_path):
    (tmp_path / "playlist").write_text(GTK3_PLAYLIST)
    out = run_jukebox(f"""
activity = jukebox({{"mime_type": "audio/x-mpegurl"}})
activity.read_file({str(tmp_path / 'playlist')!r})
print("titles", [t["title"] for t in activity.playlist.tracks])
""")
    assert "titles ['Morning song', 'Cat video']" in out


@needs_gtk4
def test_opened_from_a_song_it_never_overwrites_the_song(tmp_path):
    song = tmp_path / "song"
    song.write_bytes(b"OggS fake audio")
    out = run_jukebox(f"""
activity = jukebox({{"mime_type": "audio/ogg", "title": "Morning song"}})
activity._object_id = lambda: "1111"
activity._play_index = lambda index: None   # no audio on the host
activity.read_file({str(song)!r})
print("tracks", activity.playlist.tracks)
for step in ("single", "two"):
    if step == "two":
        activity._pick(None, "2222", "Cat video")
    try:
        activity.write_file({str(tmp_path / 'out')!r})
    except NotImplementedError:
        print("kept", step, activity.journal.saved)
""")
    assert "tracks [{'title': 'Morning song', 'path': 'journal://1111'}]" in out
    assert "kept single []" in out
    assert "kept two [('Morning song playlist', %r, 'org.laptop.sugar.Jukebox')]" % GTK3_PLAYLIST in out
    assert not (tmp_path / "out").exists()
    assert song.read_bytes() == b"OggS fake audio"


@needs_gtk4
def test_gtk4_jukebox_1_payload_keeps_only_real_files(tmp_path):
    (tmp_path / "old.json").write_text(
        '{"selected": 0, "tracks": [["Morning Bell", "Demo track"],'
        ' ["a.ogg", "Local file", "file:///home/a.ogg"]]}')
    out = run_jukebox(f"""
activity = jukebox({{"mime_type": ""}})
activity.read_file({str(tmp_path / 'old.json')!r})
print("tracks", activity.playlist.tracks)
""")
    assert "tracks [{'title': 'a.ogg', 'path': 'file:///home/a.ogg'}]" in out


@needs_gtk4
def test_corrupt_playlist_raises(tmp_path):
    (tmp_path / "bad").write_bytes(b"\xff\xfe not a valid payload")
    out = run_jukebox(f"""
try:
    jukebox({{"mime_type": "audio/x-mpegurl"}}).read_file({str(tmp_path / 'bad')!r})
except ValueError:
    print("refused")
""")
    assert "refused" in out


def test_bundle_is_registered():
    info = (PACKAGE / "activity/activity.info").read_text()
    assert "org.laptop.sugar.Jukebox" in info
    assert "sugar-activity4 jukeboxactivity4.JukeboxActivity" in info
    assert "mime_types" in info and "audio/x-mpegurl" in info and "video/mp4" in info
