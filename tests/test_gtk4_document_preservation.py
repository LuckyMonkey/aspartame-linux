"""Failed or read-only loads must never replace the original Journal payload.

See docs/DOCUMENT-PRESERVATION-PROPOSALS.md. Activities refuse a payload they
cannot open by raising from read_file(); the toolkit (0301) then keeps the
object's bytes and updates metadata only.
"""
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tests/gtk4_harness"
TOOLKIT = (ROOT / "patches/gtk4-preview/0301-toolkit-downstream-on-9d86a31.patch").read_text()


def _gtk4_usable():
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        return False
    probe = ("import gi; gi.require_version('Gtk', '4.0'); "
             "from gi.repository import Gtk; Gtk.Window()")
    return subprocess.run([sys.executable, "-c", probe], capture_output=True).returncode == 0


def _run(package, body):
    script = textwrap.dedent(f"""
        import sys
        sys.path[:0] = [{str(HARNESS)!r}, {str(ROOT / 'packages' / package)!r}]
        import gi
        gi.require_version("Gtk", "4.0")
    """) + textwrap.dedent(body)
    run = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=60)
    assert run.returncode == 0, run.stderr[-3000:]
    return run.stdout


def test_toolkit_keeps_the_payload_when_read_file_raises():
    assert "self._load_failed = True" in TOOLKIT
    assert "Activity.save: keeping the unopened payload" in TOOLKIT
    assert 'self._jobject.file_path = ""' in TOOLKIT
    assert "def load_failed(self):" in TOOLKIT


@pytest.mark.skipif(not _gtk4_usable(), reason="GTK4 or a display is unavailable")
def test_read_writes_back_the_opened_object_byte_for_byte(tmp_path):
    source = tmp_path / "write.json"
    source.write_text(json.dumps({"format": "aspartame-write-v1", "text": "Bold words",
                                  "spans": [[0, 4, "bold"]]}), encoding="utf-8")
    out = tmp_path / "out"
    _run("gtk4-read-activity", f"""
        from readactivity4 import ReadActivity
        activity = ReadActivity(None)
        activity.read_file({str(source)!r})
        activity.write_file({str(out)!r})
        try:
            ReadActivity(None).read_file({str(tmp_path / 'missing')!r})
        except OSError:
            print("refused-missing")
    """)
    assert out.read_bytes() == source.read_bytes()


@pytest.mark.skipif(not _gtk4_usable(), reason="GTK4 or a display is unavailable")
@pytest.mark.parametrize("package,module,cls", [
    ("gtk4-markdown-activity", "markdownactivity4", "MarkdownActivity"),
    ("gtk4-pippy-activity", "pippyactivity4", "PippyActivity"),
    ("gtk4-portfolio-activity", "portfolioactivity4", "PortfolioActivity"),
    ("gtk4-write-activity", "writeactivity4", "WriteActivity"),
])
def test_user_authored_activities_refuse_unreadable_payloads(tmp_path, package, module, cls):
    bad = tmp_path / "bad"
    bad.write_bytes(b"\xff\xfe\x00not utf-8")
    out = _run(package, f"""
        import importlib
        activity_class = getattr(importlib.import_module({module!r}), {cls!r})
        try:
            activity_class(None).read_file({str(bad)!r})
        except (ValueError, OSError):
            print("refused")
    """)
    assert "refused" in out


def test_record_restore_is_transactional(tmp_path):
    import zipfile
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    (store_dir / "photo-1.png").write_bytes(b"original")
    archive = tmp_path / "session.zip"
    with zipfile.ZipFile(archive, "w") as out:
        out.writestr("manifest.json", json.dumps({"version": 1, "clips": [
            {"kind": "photo", "file": "photo-1.png", "title": "new"},
            {"kind": "photo", "file": "photo-2.png", "title": "too big"}]}))
        out.writestr("media/photo-1.png", b"replacement")
        out.writestr("media/photo-2.png", b"x" * 64)
    out = _run("gtk4-record-activity", f"""
        import recordactivity4 as record
        record.MAX_SESSION_BYTES = 32  # second member exceeds the budget
        store = record.ClipStore({str(store_dir)!r})
        store.clips = [{{"kind": "photo", "file": "photo-1.png", "title": "old", "created": 0}}]
        print("loaded" if store.load({str(archive)!r}) else "refused")
        print(len(store.clips), store.clips[0]["title"])
    """)
    assert "refused" in out and "1 old" in out
    assert (store_dir / "photo-1.png").read_bytes() == b"original"
    assert sorted(path.name for path in store_dir.iterdir()) == ["photo-1.png"]
