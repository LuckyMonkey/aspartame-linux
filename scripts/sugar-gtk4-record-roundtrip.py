#!/usr/bin/env python3
"""Guest regression: resume a Record Journal object and verify its captures."""

import io
import json
import os
import struct
from pathlib import Path
import subprocess
import sys
import time
import zipfile
import zlib


BUNDLE_ID = "org.laptop.RecordActivity"
PROCESS_MARKER = "recordactivity4.RecordActivity"


def wait_for(description, callback):
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        result = callback()
        if result:
            return result
        time.sleep(0.1)
    raise RuntimeError(f"Timed out: {description}")


def tiny_png():
    """A valid 2x2 RGB PNG, so the resumed preview has a real image to load."""
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    rows = b"".join(b"\x00" + b"\xff\x80\x00" * 2 for _ in range(2))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


def seeded_session(title):
    """The Activity's Journal format: a manifest plus media, stored in a zip."""
    buffer = io.BytesIO()
    clip = {"created": 1758000000, "file": "photo-1.png", "kind": "photo", "title": title}
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(zipfile.ZipInfo("manifest.json", (1980, 1, 1, 0, 0, 0)),
                         json.dumps({"clips": [clip], "version": 1}, sort_keys=True) + "\n")
        archive.writestr(zipfile.ZipInfo("media/photo-1.png", (1980, 1, 1, 0, 0, 0)), tiny_png())
    return buffer.getvalue()


def main():
    if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text():
        raise SystemExit("Run this probe inside the Aspartame guest.")
    if os.getuid() == 0:
        pids = subprocess.check_output(
            ["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"],
            text=True,
        ).splitlines()
        if len(pids) != 1:
            raise SystemExit("Expected exactly one modern shell.")
        env = dict(
            item.split("=", 1)
            for item in Path(f"/proc/{pids[0]}/environ").read_bytes().decode().split("\0")
            if "=" in item
        )
        interpreter = "/home/aspartame/Development/gtk4-preview/venv/bin/python"
        os.setgroups([])
        os.setgid(1000)
        os.setuid(1000)
        os.execve(interpreter, [interpreter, __file__, *sys.argv[1:]], env)

    import dbus
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    bus = dbus.SessionBus()
    journal = dbus.Interface(
        bus.get_object("org.laptop.Journal", "/org/laptop/Journal"),
        "org.laptop.Journal",
    )
    shell = dbus.Interface(
        bus.get_object("org.laptop.Shell", "/org/laptop/Shell"),
        "org.laptop.Shell",
    )
    store = dbus.Interface(
        bus.get_object("org.laptop.sugar.DataStore", "/org/laptop/sugar/DataStore"),
        "org.laptop.sugar.DataStore",
    )

    def processes():
        result = []
        for path in Path("/proc").glob("[0-9]*/cmdline"):
            try:
                args = path.read_bytes().decode().split("\0")
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                continue
            if PROCESS_MARKER in args:
                result.append((int(path.parent.name), args[args.index("--activity-id") + 1]))
        return result

    def find_named(node, pid, expected, depth=0):
        if depth > 14:
            return None
        if node.get_process_id() == pid:
            try:
                visible_text = Atspi.Text.get_text(node, 0, -1)
            except Exception:
                visible_text = ""
            if expected in (node.get_name() or "") or expected in visible_text:
                return node
        for i in range(node.get_child_count()):
            child = node.get_child_at_index(i)
            if child is not None:
                found = find_named(child, pid, expected, depth + 1)
                if found is not None:
                    return found
        return None

    def launch(object_id="", expected="Take photo"):
        assert journal.LaunchBundle(BUNDLE_ID, object_id)
        pid, activity_id = wait_for("Record process", lambda: next(iter(processes()), None))
        wait_for("Activity service", lambda: bus.name_has_owner("org.laptop.Activity" + activity_id))
        wait_for("shell launch completion", lambda: shell.ActivateActivity(activity_id))
        node = wait_for(
            f"visible {expected!r}",
            lambda: find_named(Atspi.get_desktop(0), pid, expected),
        )
        return pid, activity_id, node

    def stop(pid, activity_id):
        assert shell.StopActivity(activity_id)
        wait_for("process exit", lambda: not Path(f"/proc/{pid}").exists())
        assert not bus.name_has_owner("org.laptop.Activity" + activity_id)
        assert not shell.ActivateActivity(activity_id), "stale shell activity"

    if processes():
        raise SystemExit("Record is already running; stop it before this probe.")
    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    if cycles < 1:
        raise SystemExit("cycles must be positive")

    for cycle in range(1, cycles + 1):
        title = f"Probe photo {cycle}"
        pid, activity_id, _ = launch()
        stop(pid, activity_id)
        rows, _ = store.find(
            dbus.Dictionary({"activity_id": activity_id}, signature="sv"),
            dbus.Array(["uid"], signature="s"),
        )
        assert len(rows) == 1, "expected one saved Record Journal object"
        uid = str(rows[0]["uid"])
        filename = Path(str(store.get_filename(uid)))
        filename.write_bytes(seeded_session(title))

        resumed_pid, resumed_id, _ = launch(uid, title)
        assert resumed_pid != pid
        wait_for("restore status", lambda: find_named(Atspi.get_desktop(0), resumed_pid, "Restored 1 recording."))
        stop(resumed_pid, resumed_id)
        with zipfile.ZipFile(filename) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            assert [clip["title"] for clip in manifest["clips"]] == [title]
            assert archive.read("media/photo-1.png") == tiny_png()
        print(
            f"cycle={cycle} pid={pid} resumed_pid={resumed_pid} object={uid} "
            f"clip={title!r} resume=PASS media-preserved=PASS service-release=PASS shell-cleanup=PASS",
            flush=True,
        )
    print("record-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded", flush=True)


if __name__ == "__main__":
    main()
