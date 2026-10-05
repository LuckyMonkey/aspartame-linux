#!/usr/bin/env python3
"""Qualify GTK4 Write formatting persistence and Read interoperability."""

import json
import os
from pathlib import Path
import subprocess
import time


WRITE_BUNDLE = "org.sugarlabs.Write"
WRITE_MARKER = "writeactivity4.WriteActivity"
READ_BUNDLE = "org.laptop.sugar.ReadActivity"
READ_MARKER = "readactivity4.ReadActivity"


def wait_for(description, callback):
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        value = callback()
        if value:
            return value
        time.sleep(0.1)
    raise RuntimeError(f"timed out waiting for {description}")


def reexec_as_desktop_user():
    if os.getuid() != 0:
        return
    shells = subprocess.check_output(
        ["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"],
        text=True,
    ).splitlines()
    if len(shells) != 1:
        raise RuntimeError("expected exactly one modern shell")
    environment = dict(
        item.split("=", 1)
        for item in Path(f"/proc/{shells[0]}/environ").read_bytes()
        .decode()
        .split("\0")
        if "=" in item
    )
    python = os.environ.get(
        "GTK4_PYTHON", "/usr/lib/aspartame/gtk4-preview/venv/bin/python"
    )
    os.setgroups([])
    os.setgid(1000)
    os.setuid(1000)
    os.execve(python, [python, __file__], environment)


def main():
    reexec_as_desktop_user()
    if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text():
        raise SystemExit("Run inside Aspartame guest")
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

    def processes(marker):
        found = []
        for command_path in Path("/proc").glob("[0-9]*/cmdline"):
            try:
                args = command_path.read_bytes().decode().split("\0")
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                continue
            if marker in args and "--activity-id" in args:
                found.append((int(command_path.parent.name), args[args.index("--activity-id") + 1]))
        return found

    def find_text(node, pid, expected, depth=0):
        if depth > 16:
            return None
        if node.get_process_id() == pid:
            try:
                visible = Atspi.Text.get_text(node, 0, -1)
            except Exception:
                visible = ""
            if expected in visible or expected in (node.get_name() or ""):
                return node
        for index in range(node.get_child_count()):
            child = node.get_child_at_index(index)
            if child is not None:
                found = find_text(child, pid, expected, depth + 1)
                if found is not None:
                    return found
        return None

    def find_button(node, pid, expected, depth=0):
        if depth > 16:
            return None
        if node.get_process_id() == pid and node.get_role_name() in ("button", "push button"):
            label = node.get_name() or ""
            try:
                label += " " + (node.get_description() or "")
            except Exception:
                pass
            if expected in label:
                return node
        for index in range(node.get_child_count()):
            child = node.get_child_at_index(index)
            if child is not None:
                found = find_button(child, pid, expected, depth + 1)
                if found is not None:
                    return found
        return None

    def launch(bundle, marker, object_id="", expected=""):
        if not journal.LaunchBundle(bundle, object_id):
            raise RuntimeError(f"Journal refused {bundle}")
        pid, activity_id = wait_for(
            f"{bundle} process", lambda: next(iter(processes(marker)), None)
        )
        wait_for(
            f"{bundle} service",
            lambda: bus.name_has_owner(f"org.laptop.Activity{activity_id}"),
        )
        if not shell.ActivateActivity(activity_id):
            raise RuntimeError(f"Shell refused {activity_id}")
        node = wait_for(
            f"{bundle} visible content",
            lambda: find_text(Atspi.get_desktop(0), pid, expected),
        )
        return pid, activity_id, node

    def stop(pid, activity_id):
        if not shell.StopActivity(activity_id):
            raise RuntimeError(f"Shell refused stop for {activity_id}")
        wait_for(f"cleanup {activity_id}", lambda: not Path(f"/proc/{pid}").exists())
        if bus.name_has_owner(f"org.laptop.Activity{activity_id}"):
            raise RuntimeError(f"Activity service remained owned: {activity_id}")

    if processes(WRITE_MARKER) or processes(READ_MARKER):
        raise SystemExit("Write or Read is already running; stop it before this probe.")

    content = "Formatted Aspartame note"
    pid, activity_id, document = launch(WRITE_BUNDLE, WRITE_MARKER, expected="Document text")
    assert Atspi.EditableText.set_text_contents(document, content)
    select_all = wait_for(
        "Select all action",
        lambda: find_button(Atspi.get_desktop(0), pid, "Select all"),
    )
    assert select_all and select_all.get_n_actions() and select_all.get_action().do_action(0)
    bold = wait_for(
        "Bold action",
        lambda: find_button(Atspi.get_desktop(0), pid, "Bold"),
    )
    assert bold and bold.get_n_actions() and bold.get_action().do_action(0)
    wait_for("bold status", lambda: find_text(Atspi.get_desktop(0), pid, "Applied bold formatting"))
    stop(pid, activity_id)

    rows, _ = store.find(
        dbus.Dictionary({"activity_id": activity_id}, signature="sv"),
        dbus.Array(["uid"], signature="s"),
    )
    if len(rows) != 1:
        raise RuntimeError("expected one formatted Journal object")
    uid = str(rows[0]["uid"])
    filename = Path(str(store.get_filename(uid)))
    payload = json.loads(filename.read_text(encoding="utf-8"))
    assert payload["format"] == "aspartame-write-v1"
    assert payload["text"] == content
    assert any("bold" in span["tags"] for span in payload["spans"])

    write_pid, write_activity, _ = launch(WRITE_BUNDLE, WRITE_MARKER, uid, content)
    stop(write_pid, write_activity)
    read_pid, read_activity, _ = launch(READ_BUNDLE, READ_MARKER, uid, content)
    stop(read_pid, read_activity)
    print(
        "write-format-roundtrip=PASS bold-persist=PASS read-interoperability=PASS cleanup=PASS",
        flush=True,
    )


if __name__ == "__main__":
    main()
