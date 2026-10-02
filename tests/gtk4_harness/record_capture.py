"""Capture photo, video and audio with the GTK4 Record Activity, then resume.

Runs in its own process with GStreamer test sources standing in for a camera
and microphone.  Prints ``record-capture=PASS`` on success.
"""

import os
import sys
import tempfile
import time
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "packages/gtk4-record-activity"))
os.environ["ASPARTAME_RECORD_VIDEO_SOURCE"] = "videotestsrc is-live=true"
os.environ["ASPARTAME_RECORD_AUDIO_SOURCE"] = "audiotestsrc is-live=true"

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")
from gi.repository import GLib  # noqa: E402

import recordactivity4  # noqa: E402

SIGNATURES = {"photo": b"\x89PNG\r\n\x1a\n", "video": b"\x1aE\xdf\xa3", "audio": b"OggS"}


def spin_until(predicate, seconds=15):
    context = GLib.MainContext.default()
    deadline = time.monotonic() + seconds
    while not predicate():
        if time.monotonic() > deadline:
            raise AssertionError("timed out waiting for capture")
        context.iteration(False)
        time.sleep(0.01)


def capture(activity, mode, seconds=0.0):
    before = len(activity.store.clips)
    activity.mode_buttons[mode].set_active(True)
    assert activity.capture.get_sensitive(), activity.status.get_text()
    activity.capture.emit("clicked")
    if mode != "photo":
        spin_until(lambda: activity.recorder is not None)
        assert activity.capture.get_label() == "Stop recording"
        end = time.monotonic() + seconds
        spin_until(lambda: time.monotonic() >= end)
        activity.capture.emit("clicked")
    spin_until(lambda: activity.recorder is None)
    assert len(activity.store.clips) == before + 1, activity.status.get_text()
    clip = activity.store.clips[-1]
    data = activity.store.path(clip).read_bytes()
    assert data.startswith(SIGNATURES[mode]), (mode, data[:8])
    return clip


def main():
    activity = recordactivity4.RecordActivity(None)
    for mode, seconds in (("photo", 0), ("video", 1.0), ("audio", 1.0), ("photo", 0)):
        capture(activity, mode, seconds)
    titles = [clip["title"] for clip in activity.store.clips]
    assert titles == ["Photo 1", "Video 1", "Audio 1", "Photo 2"], titles

    activity.gallery.select_row(activity.gallery.get_row_at_index(1))
    assert activity.preview.get_visible_child_name() == "media"
    activity.gallery.select_row(activity.gallery.get_row_at_index(0))
    assert activity.preview.get_visible_child_name() == "picture"

    with tempfile.TemporaryDirectory() as tmp:
        saved, again = Path(tmp, "saved"), Path(tmp, "again")
        activity.write_file(str(saved))
        originals = {c["file"]: activity.store.path(c).read_bytes() for c in activity.store.clips}

        resumed = recordactivity4.RecordActivity(None)
        resumed.read_file(str(saved))
        assert [c["title"] for c in resumed.store.clips] == titles
        for clip in resumed.store.clips:
            assert resumed.store.path(clip).read_bytes() == originals[clip["file"]]
        resumed.write_file(str(again))
        assert saved.read_bytes() == again.read_bytes()

        # Removing a capture deletes its media and drops it from the next save.
        resumed.gallery.select_row(resumed.gallery.get_row_at_index(1))
        removed = resumed.store.path(resumed.store.clips[1])
        resumed.remove.emit("clicked")
        assert not removed.exists()
        resumed.write_file(str(again))
        with zipfile.ZipFile(again) as archive:
            assert "media/video-1.webm" not in archive.namelist()

        # A hostile manifest cannot write outside the store or crash resume.
        hostile = Path(tmp, "hostile")
        with zipfile.ZipFile(hostile, "w") as archive:
            archive.writestr("manifest.json", '{"clips": [{"kind": "photo", "file": "../escape.png"},'
                             ' {"kind": "photo", "file": "ok.png"}, {"kind": "photo", "file": "ok.png"}]}')
            archive.writestr("media/../escape.png", b"x")
            archive.writestr("media/ok.png", b"\x89PNG\r\n\x1a\n")
        victim = recordactivity4.RecordActivity(None)
        victim.read_file(str(hostile))
        assert [c["file"] for c in victim.store.clips] == ["ok.png"]
        assert not (victim.store.directory.parent / "escape.png").exists()
    print("record-capture=PASS")


if __name__ == "__main__":
    main()
