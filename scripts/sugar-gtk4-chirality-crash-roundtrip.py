#!/usr/bin/env python3
"""Qualify GTK4 Chirality cleanup when the held Activity crashes."""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parent
ADAPTER = ROOT / "sugar-chirality-activity.py"
CASES = (
    ("org.aspartame.Calculate", "calculateactivity4.CalculateActivity"),
    ("tv.alterna.Clock", "clockactivity4.ClockActivity"),
)
CALCULATE_BUNDLE = CASES[0][0]
CLOCK_BUNDLE = CASES[1][0]


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
    import dbus

    bus = dbus.SessionBus()
    journal = dbus.Interface(
        bus.get_object("org.laptop.Journal", "/org/laptop/Journal"),
        "org.laptop.Journal",
    )
    shell = dbus.Interface(
        bus.get_object("org.laptop.Shell", "/org/laptop/Shell"),
        "org.laptop.Shell",
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

    def launch(bundle, marker):
        if not journal.LaunchBundle(bundle, ""):
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
        return pid, activity_id

    def stop(pid, activity_id):
        if not Path(f"/proc/{pid}").exists():
            return
        if not shell.StopActivity(activity_id):
            raise RuntimeError(f"Shell refused stop for {activity_id}")
        wait_for(f"cleanup {activity_id}", lambda: not Path(f"/proc/{pid}").exists())
        if bus.name_has_owner(f"org.laptop.Activity{activity_id}"):
            raise RuntimeError(f"Activity service remained owned: {activity_id}")

    def run_adapter(state, *args):
        result = subprocess.run(
            [sys.executable, str(ADAPTER), "--state-file", str(state), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    markers = [marker for _bundle, marker in CASES]
    if any(processes(marker) for marker in markers):
        raise SystemExit("Calculate or Clock is already running; stop it before this probe.")

    live = []
    with tempfile.TemporaryDirectory(prefix="chirality-crash-") as directory:
        state = Path(directory) / "chirality.json"
        try:
            activities = [launch(bundle, marker) for bundle, marker in CASES]
            live.extend(activities)
            run_adapter(
                state, "assign", "left", activities[0][1],
                "--bundle-id", CALCULATE_BUNDLE,
            )
            run_adapter(
                state, "assign", "right", activities[1][1],
                "--bundle-id", CLOCK_BUNDLE,
            )
            active = run_adapter(state, "activate", "left")
            assert active["active_hand"] == "left"

            crashed_pid, crashed_id = activities[1]
            os.kill(crashed_pid, signal.SIGKILL)
            wait_for(
                f"crashed process {crashed_pid} exit",
                lambda: not Path(f"/proc/{crashed_pid}").exists(),
            )
            wait_for(
                f"crashed service {crashed_id} release",
                lambda: not bus.name_has_owner(f"org.laptop.Activity{crashed_id}"),
            )
            live.remove((crashed_pid, crashed_id))

            recovered = run_adapter(state, "activity-exited", crashed_id)
            assert recovered["active_hand"] == "left"
            assert recovered["hands"][0]["activity_id"] == activities[0][1]
            assert recovered["hands"][1]["activity_id"] is None
            assert Path(f"/proc/{activities[0][0]}").exists()
            assert bus.name_has_owner(f"org.laptop.Activity{activities[0][1]}")
            still_active = run_adapter(state, "activate", "left")
            assert still_active["active_hand"] == "left"

            stop(*activities[0])
            live.remove(activities[0])
            finished = run_adapter(state, "activity-exited", activities[0][1])
            assert finished["active_hand"] is None
            assert all(hand["activity_id"] is None for hand in finished["hands"])
            print(
                "chirality-crash-roundtrip=PASS "
                "crashed=right preserved=left active=left "
                "state-clean=PASS mode=single-surface",
                flush=True,
            )
        finally:
            for pid, activity_id in reversed(live):
                try:
                    stop(pid, activity_id)
                except Exception:
                    pass


if __name__ == "__main__":
    main()
