#!/usr/bin/env python3
"""Run deterministic keyboard/mouse macros against the Aspartame QEMU window.

The guest display is a normal X11 window, so host-side xdotool is both faster
and more repeatable than hand-clicking through a long visual test.  Macros are
JSON arrays, for example::

    [
      {"action": "activate"},
      {"action": "key", "keys": "F8"},
      {"action": "sleep", "seconds": 1},
      {"action": "click", "x": 640, "y": 420},
      {"action": "screenshot", "path": "reports/screenshots/space.png"}
    ]

No shell is involved in executing a step.  That keeps test macros inspectable
and prevents coordinates or typed text from becoming command input.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any


DEFAULT_WINDOW = r"^QEMU \(Aspartame\)$"
ACTION_NAMES = {"activate", "click", "key", "move", "sleep", "screenshot", "text"}


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run one xdotool/import command without invoking a shell."""

    return subprocess.run(args, check=check, text=True, capture_output=True)


def find_window(pattern: str) -> str:
    # QEMU can remain alive with its GTK window unmapped after a monitor/HMP
    # probe. Find it regardless of map state; the activate action below makes
    # it visible before delivering input.
    result = run("xdotool", "search", "--name", pattern, check=False)
    windows = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if result.returncode or not windows:
        detail = result.stderr.strip() or "no matching visible window"
        raise RuntimeError(f"could not find QEMU window {pattern!r}: {detail}")
    return windows[-1]


def number(step: dict[str, Any], key: str, *, integer: bool = False) -> str:
    value = step.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key!r} must be a number")
    if integer and int(value) != value:
        raise ValueError(f"{key!r} must be an integer")
    return str(int(value) if integer else value)


def run_step(step: dict[str, Any], window: str) -> None:
    action = step.get("action")
    if action not in ACTION_NAMES:
        raise ValueError(f"unknown macro action: {action!r}")

    if action == "activate":
        run("xdotool", "windowmap", "--sync", window, check=False)
        run("xdotool", "windowactivate", "--sync", window)
        run("xdotool", "windowfocus", window)
    elif action == "key":
        keys = step.get("keys")
        if not isinstance(keys, str) or not keys.strip():
            raise ValueError("key action requires non-empty string 'keys'")
        run("xdotool", "key", "--clearmodifiers", "--window", window, keys)
    elif action == "text":
        value = step.get("text")
        if not isinstance(value, str):
            raise ValueError("text action requires string 'text'")
        # Text input follows the pointer/focus established by activate or a
        # preceding click. Unlike key, xdotool's --window type path can bypass
        # QEMU's emulated keyboard focus.
        run("xdotool", "type", "--clearmodifiers", value)
    elif action == "move":
        run("xdotool", "mousemove", "--window", window,
            number(step, "x", integer=True), number(step, "y", integer=True))
    elif action == "click":
        button = number(step, "button", integer=True) if "button" in step else "1"
        run("xdotool", "mousemove", "--window", window,
            number(step, "x", integer=True), number(step, "y", integer=True))
        # QEMU consumes the XTest pointer event at the current host pointer;
        # targeting the window on the click command itself can skip the
        # emulated tablet path.
        run("xdotool", "click", button)
    elif action == "sleep":
        seconds = step.get("seconds", 0.2)
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or seconds < 0:
            raise ValueError("sleep seconds must be a non-negative number")
        time.sleep(seconds)
    elif action == "screenshot":
        path = step.get("path")
        if not isinstance(path, str) or not path:
            raise ValueError("screenshot action requires string 'path'")
        output = Path(path).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        run("import", "-window", window, str(output))
        if not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError(f"screenshot was not created: {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("macro", type=Path, help="JSON file containing an array of macro steps")
    parser.add_argument("--window-name", default=DEFAULT_WINDOW,
                        help="xdotool window-name pattern (default: %(default)s)")
    parser.add_argument("--display", help="X11 display override, e.g. :0")
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat must be positive")
    if not shutil.which("xdotool") or not shutil.which("import"):
        parser.error("qemu-macro requires xdotool and ImageMagick import")

    try:
        payload = json.loads(args.macro.read_text())
        if not isinstance(payload, list):
            raise ValueError("macro root must be a JSON array")
        steps = payload
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                raise ValueError(f"step {index} must be an object")
        if args.display:
            os.environ["DISPLAY"] = args.display
        window = find_window(args.window_name)
        for _ in range(args.repeat):
            for index, step in enumerate(steps):
                try:
                    run_step(step, window)
                except Exception as error:
                    raise RuntimeError(f"step {index} ({step.get('action')!r}) failed: {error}") from error
    except (OSError, json.JSONDecodeError, ValueError, RuntimeError) as error:
        print(f"qemu-macro: {error}", file=sys.stderr)
        return 1
    print(f"qemu-macro=PASS steps={len(steps)} repeats={args.repeat} window={window}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
