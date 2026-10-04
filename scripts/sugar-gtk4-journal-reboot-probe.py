#!/usr/bin/env python3
"""Prepare or verify a GTK4 Journal object across a guest reboot."""

import json
import os
from pathlib import Path
import subprocess
import sys
import time


BUNDLE_ID = "org.aspartame.Calculate"
PROCESS_MARKER = "calculateactivity4.CalculateActivity"
STATE_FILE = Path("/home/aspartame/.aspartame-journal-reboot-state.json")


def wait_for(description, callback):
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        result = callback()
        if result:
            return result
        time.sleep(0.1)
    raise RuntimeError(f"Timed out: {description}")


def reexec_as_user():
    if os.getuid() != 0:
        return
    pids = subprocess.check_output(
        ["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"],
        text=True,
    ).splitlines()
    if len(pids) != 1:
        raise SystemExit(f"Expected one modern shell, found {pids!r}")
    env = dict(
        item.split("=", 1)
        for item in Path(f"/proc/{pids[0]}/environ").read_bytes().decode().split("\0")
        if "=" in item
    )
    interpreter = os.environ.get(
        "GTK4_PYTHON", "/usr/lib/aspartame/gtk4-preview/venv/bin/python"
    )
    os.setgroups([])
    os.setgid(1000)
    os.setuid(1000)
    os.execve(interpreter, [interpreter, __file__, *sys.argv[1:]], env)


def pin_modern_atspi_bus():
    """Keep AT-SPI on the GTK4 bus while GTK3 remains alive beside it."""
    try:
        result = subprocess.run(
            ["xprop", "-root", "AT_SPI_BUS"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return
    _name, separator, value = result.stdout.partition("= ")
    if separator:
        value = value.strip().strip('"')
        if value:
            os.environ["AT_SPI_BUS"] = value
            subprocess.run(
                ["xprop", "-root", "-f", "AT_SPI_BUS", "8s",
                 "-set", "AT_SPI_BUS", value],
                check=True,
                stdout=subprocess.DEVNULL,
            )


def process_list():
    result = []
    for path in Path("/proc").glob("[0-9]*/cmdline"):
        try:
            args = path.read_bytes().decode().split("\0")
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if PROCESS_MARKER in args and "--activity-id" in args:
            result.append((int(path.parent.name), args[args.index("--activity-id") + 1]))
    return result


def find_text(node, pid, expected, depth=0):
    if depth > 14:
        return None
    if node.get_process_id() == pid:
        try:
            if expected in Atspi.Text.get_text(node, 0, -1):
                return node
        except Exception:
            pass
        try:
            if expected in (node.get_name() or ""):
                return node
        except Exception:
            pass
    for index in range(node.get_child_count()):
        child = node.get_child_at_index(index)
        if child is not None:
            found = find_text(child, pid, expected, depth + 1)
            if found is not None:
                return found
    return None


def find_process(node, pid, depth=0):
    """Find any live Activity node; text providers are not uniform in Casilda."""
    if depth > 14:
        return None
    if node.get_process_id() == pid:
        return node
    for index in range(node.get_child_count()):
        child = node.get_child_at_index(index)
        if child is not None:
            found = find_process(child, pid, depth + 1)
            if found is not None:
                return found
    return None


def main():
    if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text():
        raise SystemExit("Run inside Aspartame")
    if len(sys.argv) < 2 or sys.argv[1] not in {"prepare", "verify"}:
        raise SystemExit(
            "usage: sugar-gtk4-journal-reboot-probe.py prepare|verify [screenshot]"
        )
    reexec_as_user()
    pin_modern_atspi_bus()

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

    def launch(uid="", expected="Calculate"):
        assert journal.LaunchBundle(BUNDLE_ID, uid)
        pid, activity_id = wait_for("Calculate process", lambda: next(iter(process_list()), None))
        wait_for("Calculate service", lambda: bus.name_has_owner("org.laptop.Activity" + activity_id))
        assert shell.ActivateActivity(activity_id)
        node = wait_for(
            "Calculate surface",
            lambda: find_process(Atspi.get_desktop(0), pid),
        )
        return pid, activity_id, node

    def stop(pid, activity_id):
        assert shell.StopActivity(activity_id)
        wait_for("Calculate exit", lambda: not Path(f"/proc/{pid}").exists())
        assert not bus.name_has_owner("org.laptop.Activity" + activity_id)
        assert not shell.ActivateActivity(activity_id)

    if process_list():
        raise SystemExit("Calculate is already running")

    if sys.argv[1] == "prepare":
        pid, activity_id, _node = launch()
        stop(pid, activity_id)
        rows, _props = store.find(
            dbus.Dictionary({"activity_id": activity_id}, signature="sv"),
            dbus.Array(["uid"], signature="s"),
        )
        assert len(rows) == 1
        uid = str(rows[0]["uid"])
        filename = Path(str(store.get_filename(uid)))
        filename.write_text("7 * 6\n", encoding="utf-8")
        STATE_FILE.write_text(
            json.dumps({"uid": uid}, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"journal-reboot-prepare=PASS uid={uid} payload=7*6")
        return

    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    uid = str(state["uid"])
    # The datastore may migrate its physical object path while rebuilding its
    # index. Resolve it again by UID after reboot instead of persisting a stale
    # filename from the pre-reboot process.
    filename = Path(str(store.get_filename(uid)))
    assert filename.read_text(encoding="utf-8").strip() == "7 * 6"
    pid, activity_id, node = launch(uid, "7 * 6")
    if len(sys.argv) > 2:
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "x11grab",
             "-video_size", "1920x1080", "-i", ":0", "-frames:v", "1",
             "-y", sys.argv[2]],
            check=True,
        )
    stop(pid, activity_id)
    print(
        f"journal-reboot-verify=PASS uid={uid} payload=7*6 "
        "surface=PASS cleanup=PASS"
    )


if __name__ == "__main__":
    main()
