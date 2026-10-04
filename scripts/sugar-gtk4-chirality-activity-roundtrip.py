#!/usr/bin/env python3
"""Guest qualification for two persistent GTK4 Activities in Chirality."""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


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
    python = os.environ.get("GTK4_PYTHON", "/usr/lib/aspartame/gtk4-preview/venv/bin/python")
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
            if marker in args:
                found.append((int(command_path.parent.name), args[args.index("--activity-id") + 1]))
        return found

    def launch(bundle, marker):
        if not journal.LaunchBundle(bundle, ""):
            raise RuntimeError(f"Journal refused {bundle}")
        pid, activity_id = wait_for(f"{bundle} process", lambda: next(iter(processes(marker)), None))
        wait_for(
            f"{bundle} service",
            lambda: bus.name_has_owner(f"org.laptop.Activity{activity_id}"),
        )
        return pid, activity_id

    def run_adapter(state, *args):
        result = subprocess.run(
            [sys.executable, str(ADAPTER), "--state-file", str(state), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    activities = []
    with tempfile.TemporaryDirectory(prefix="chirality-activity-") as directory:
        state = Path(directory) / "chirality.json"
        try:
            for bundle, marker in CASES:
                activities.append(launch(bundle, marker))
            run_adapter(
                state, "assign", "left", activities[0][1],
                "--bundle-id", CALCULATE_BUNDLE,
            )
            run_adapter(
                state, "assign", "right", activities[1][1],
                "--bundle-id", CLOCK_BUNDLE,
            )
            active_sequence = []
            for selected in ("left", "right", "left"):
                payload = run_adapter(state, "activate", selected)
                active_sequence.append(payload["active_hand"])
            assert active_sequence == ["left", "right", "left"]
            final = run_adapter(state, "inspect")
            assert final["hands"][0]["activity_id"] == activities[0][1]
            assert final["hands"][1]["activity_id"] == activities[1][1]
            print(
                "chirality-activity-roundtrip=PASS "
                f"active-sequence={','.join(active_sequence)} "
                "mode=single-surface",
                flush=True,
            )
        finally:
            for _pid, activity_id in activities:
                shell.StopActivity(activity_id)
            for pid, activity_id in activities:
                wait_for(f"cleanup {activity_id}", lambda pid=pid: not Path(f"/proc/{pid}").exists())
                if bus.name_has_owner(f"org.laptop.Activity{activity_id}"):
                    raise RuntimeError(f"Activity service remained owned: {activity_id}")


if __name__ == "__main__":
    main()
