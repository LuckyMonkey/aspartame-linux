"""Exercise one native GTK4 Activity bundle headlessly and report as JSON.

Usage: python roundtrip.py <packages/gtk4-*-activity>

Runs in its own process (GTK3 and GTK4 cannot share a GI namespace) with the
``sugar4`` stub from this directory on ``sys.path``.  Checks, in order:

1. the Activity class named by ``activity.info`` constructs;
2. every sensitive button can be clicked without a callback traceback;
3. after that interaction, ``write_file`` -> fresh instance ``read_file`` ->
   ``write_file`` reproduces the same bytes (Journal resume is lossless);
4. ``read_file`` tolerates empty, malformed, and wrong-shaped objects and the
   Activity can still save afterwards.
"""

import configparser
import importlib
import json
import sys
import tempfile
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk  # noqa: E402

MALFORMED = (b"", b"not json", b"[]", b"null", b"42", b'{"unexpected": true}',
             b'{"state": {"nested": [1, 2, 3]}}', b"\xff\xfe\x00garbage")

callback_errors = []


def _record_callback_error(exc_type, exc, tb):
    callback_errors.append("".join(traceback.format_exception(exc_type, exc, tb)))


def _activity_class(package):
    info = configparser.ConfigParser()
    info.read(package / "activity" / "activity.info")
    target = info["Activity"]["exec"].split()[-1]
    module_name, class_name = target.rsplit(".", 1)
    sys.path.insert(0, str(package))
    return getattr(importlib.import_module(module_name), class_name)


def _buttons(widget):
    child = widget.get_first_child()
    while child is not None:
        if isinstance(child, Gtk.Button):
            yield child
        yield from _buttons(child)
        child = child.get_next_sibling()


def _drain():
    context = GLib.MainContext.default()
    for _ in range(50):
        if not context.iteration(False):
            break


def _overrides(cls, name):
    from sugar4.activity import SimpleActivity
    return getattr(cls, name, None) is not getattr(SimpleActivity, name)


def main(package):
    package = Path(package).resolve()
    result = {"package": package.name, "checks": {}, "errors": []}
    sys.excepthook = _record_callback_error
    cls = _activity_class(package)
    activity = cls(None)
    result["checks"]["construct"] = True

    clicked = 0
    for button in list(_buttons(activity)):
        if button.get_sensitive() and button.get_visible():
            button.emit("clicked")
            clicked += 1
            _drain()
    result["checks"]["buttons_clicked"] = clicked

    persistent = _overrides(cls, "write_file") and _overrides(cls, "read_file")
    result["checks"]["persistent"] = persistent
    if persistent:
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp, "first"), Path(tmp, "second")
            activity.write_file(str(first))
            resumed = cls(None)
            resumed.read_file(str(first))
            resumed.write_file(str(second))
            same = first.read_bytes() == second.read_bytes()
            result["checks"]["roundtrip_stable"] = same
            if not same:
                result["errors"].append(
                    "resume changed saved state:\n  saved:   %r\n  resumed: %r"
                    % (first.read_bytes()[:400], second.read_bytes()[:400]))

            tolerated = True
            for payload in MALFORMED:
                bad = Path(tmp, "bad")
                bad.write_bytes(payload)
                try:
                    victim = cls(None)
                    victim.read_file(str(bad))
                    victim.write_file(str(Path(tmp, "after-bad")))
                except Exception as exc:  # report every failing shape
                    tolerated = False
                    result["errors"].append(
                        "malformed object %r: %s: %s" % (payload, type(exc).__name__, exc))
            result["checks"]["malformed_tolerated"] = tolerated

    _drain()
    result["errors"].extend(callback_errors)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1]))
    except Exception:
        sys.excepthook = sys.__excepthook__
        traceback.print_exc()
        sys.exit(1)
