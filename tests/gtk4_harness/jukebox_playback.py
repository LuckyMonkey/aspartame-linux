"""Play a real local Ogg file in the GTK4 Jukebox and resume it from Journal.

Prints ``jukebox-playback=PASS``.  Needs GTK4's media backend (GStreamer).
"""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "packages/gtk4-jukebox-activity"))

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")
gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst  # noqa: E402

import jukeboxactivity4  # noqa: E402


def spin_until(predicate, seconds=10):
    context = GLib.MainContext.default()
    deadline = time.monotonic() + seconds
    while not predicate():
        if time.monotonic() > deadline:
            raise AssertionError("timed out")
        context.iteration(False)
        time.sleep(0.01)


def main():
    tmp = Path(tempfile.mkdtemp())
    song = tmp / "tone.ogg"
    Gst.init(None)
    pipeline = Gst.parse_launch(
        "audiotestsrc num-buffers=40 ! audioconvert ! vorbisenc ! oggmux ! filesink location=%s" % song)
    pipeline.set_state(Gst.State.PLAYING)
    pipeline.get_bus().timed_pop_filtered(10 * Gst.SECOND, Gst.MessageType.EOS | Gst.MessageType.ERROR)
    pipeline.set_state(Gst.State.NULL)
    assert song.stat().st_size > 0

    activity = jukeboxactivity4.JukeboxActivity(None)
    activity._tracks.append((song.name, jukeboxactivity4.LOCAL_DETAIL, str(song)))
    activity._selected = len(activity._tracks) - 1
    activity._refresh_playlist()
    activity._play_selected(None)
    assert activity._media is not None
    spin_until(lambda: activity._media is None or activity._media.get_playing()
               or activity._media.get_ended())
    assert "Playing: tone.ogg" in activity.status.get_text() or "Finished" in activity.status.get_text(), activity.status.get_text()
    spin_until(lambda: "Finished: tone.ogg" in activity.status.get_text(), 15)
    assert activity.play.get_sensitive()

    # Demo tracks stay honest about having no audio.
    activity._selected = 0
    activity._refresh_playlist()
    activity._play_selected(None)
    assert "demo track, no audio" in activity.status.get_text()
    activity._stop(None)

    saved = tmp / "journal"
    activity.write_file(str(saved))
    tracks = json.loads(saved.read_text())["tracks"]
    assert tracks[-1] == [song.name, "Local file", str(song)]
    resumed = jukeboxactivity4.JukeboxActivity(None)
    resumed.read_file(str(saved))
    assert resumed._tracks[-1][2] == str(song)

    # Objects saved before playback support still load.
    old = tmp / "old"
    old.write_text('{"tracks":[["Field Recording","Local file · playback backend pending"]],"selected":0}\n')
    legacy = jukeboxactivity4.JukeboxActivity(None)
    legacy.read_file(str(old))
    assert legacy._tracks == [("Field Recording", "Local file · playback backend pending")]

    song.unlink()
    resumed.playlist.select_row(resumed.playlist.get_row_at_index(len(resumed._tracks) - 1))
    resumed._play_selected(None)
    assert "no longer there" in resumed.status.get_text()
    print("jukebox-playback=PASS")


if __name__ == "__main__":
    main()
