#!/usr/bin/env python3
"""Run keyboard/pointer/screenshot macros through a headless QEMU QMP socket.

This is the default automation path for the VM. It never searches for,
activates, maps, or clicks a host window. A macro is a JSON array such as::

    [
      {"action": "key", "keys": "F8"},
      {"action": "sleep", "seconds": 1},
      {"action": "screenshot", "path": "reports/qemu-home.png"}
    ]

Keyboard events use QEMU's monitor ``sendkey`` route; pointer events use the
absolute USB-tablet route. Screenshots use QEMU's framebuffer ``screendump``.
For a screenshot of the composited guest X display, use the existing
``sugar-screenshot.sh`` SSH helper after the macro.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socket
import shutil
import subprocess
import time
from typing import Any


QMP_DEFAULT = "/tmp/aspartame-qemu-qmp-headless"
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
KEYCODES = {f"F{i}": f"f{i}" for i in range(1, 13)}
KEYCODES.update({letter: letter.lower() for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"})
KEYCODES.update({str(i): str(i) for i in range(10)})
KEYCODES.update({
    "TAB": "tab", "ENTER": "ret", "RETURN": "ret", "ESC": "esc",
    "SPACE": "spc", "BACKSPACE": "backspace", "DELETE": "delete",
    "PERIOD": "dot", ".": "dot", "MINUS": "minus", "-": "minus",
    "EQUAL": "equal", "=": "equal",
})


def qcode_for(key: str) -> str:
    normalized = key.strip().upper()
    if normalized not in KEYCODES:
        raise ValueError(f"unsupported QEMU key: {key!r}")
    return KEYCODES[normalized]


def hmp_key_for(keys: str) -> str:
    parts = [part for part in keys.upper().split("+") if part]
    if not parts:
        raise ValueError("key action requires non-empty string 'keys'")
    converted = []
    for part in parts:
        if part in {"CTRL", "CONTROL"}:
            converted.append("ctrl")
        elif part == "SHIFT":
            converted.append("shift")
        elif part == "ALT":
            converted.append("alt")
        else:
            converted.append(qcode_for(part))
    return "-".join(converted)


def text_keys(value: str) -> list[str]:
    result = []
    for character in value:
        if character.isalpha() and character.isupper():
            result.append(f"shift-{qcode_for(character)}")
        elif character.isalpha() or character.isdigit():
            result.append(qcode_for(character))
        elif character == "+":
            result.append("shift-equal")
        elif character in ".-=":
            result.append(qcode_for(character))
        elif character == " ":
            result.append("spc")
        else:
            raise ValueError(f"unsupported text character: {character!r}")
    return result


class Qmp:
    def __init__(self, path: str):
        self.sock = socket.socket(socket.AF_UNIX)
        self.sock.settimeout(5)
        self.sock.connect(path)
        self._read_object()  # greeting
        self.command("qmp_capabilities")

    def _read_object(self) -> dict[str, Any]:
        data = b""
        while b"\n" not in data:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("QMP socket closed")
            data += chunk
        line, _, remainder = data.partition(b"\n")
        # QMP normally emits one JSON object per read. Keep the implementation
        # deliberately small; commands in this runner are synchronous.
        if remainder:
            raise RuntimeError("unexpected buffered QMP response")
        return json.loads(line.decode())

    def command(self, execute: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"execute": execute}
        if arguments:
            payload["arguments"] = arguments
        self.sock.sendall((json.dumps(payload) + "\n").encode())
        while True:
            reply = self._read_object()
            if "event" in reply:
                continue
            if "error" in reply:
                raise RuntimeError(reply["error"].get("desc", str(reply["error"])))
            return reply

    def key(self, keys: str, device: str | None = None) -> None:
        if device:
            qcodes = [qcode_for(part) for part in keys.upper().split("+") if part not in {"CTRL", "CONTROL", "SHIFT", "ALT"}]
            modifiers = [part for part in keys.upper().split("+") if part in {"CTRL", "CONTROL", "SHIFT", "ALT"}]
            qcodes = [qcode_for(modifier) if modifier not in {"CTRL", "CONTROL", "SHIFT", "ALT"} else {"CTRL": "ctrl", "CONTROL": "ctrl", "SHIFT": "shift", "ALT": "alt"}[modifier] for modifier in modifiers] + qcodes
            events = [{"type": "key", "data": {"down": True, "key": {"type": "qcode", "data": qcode}}} for qcode in qcodes]
            events += [{"type": "key", "data": {"down": False, "key": {"type": "qcode", "data": qcode}}} for qcode in reversed(qcodes)]
            self.command("input-send-event", {"device": device, "events": events})
            return
        self.command("human-monitor-command", {"command-line": f"sendkey {hmp_key_for(keys)}"})

    def type_text(self, value: str, device: str | None = None) -> None:
        for key in text_keys(value):
            self.key(key.replace("-", "+"), device)

    def click(self, x: int, y: int, device: str | None) -> None:
        x = max(0, min(x, SCREEN_WIDTH))
        y = max(0, min(y, SCREEN_HEIGHT))
        # Keep button release in a separate QMP command.  The guest input
        # stack needs an event-loop boundary between press and release for a
        # GTK click gesture to emit ``clicked``; batching both events only
        # focused the widget in headless runs.
        events: list[dict[str, Any]] = [
            {"type": "abs", "data": {"axis": "x", "value": round(x * 32767 / SCREEN_WIDTH)}},
            {"type": "abs", "data": {"axis": "y", "value": round(y * 32767 / SCREEN_HEIGHT)}},
            {"type": "btn", "data": {"button": "left", "down": True}},
        ]
        arguments: dict[str, Any] = {"events": events}
        if device:
            arguments["device"] = device
        self.command("input-send-event", arguments)
        release: dict[str, Any] = {
            "events": [{"type": "btn", "data": {"button": "left", "down": False}}]
        }
        if device:
            release["device"] = device
        self.command("input-send-event", release)

    def drag(self, x1: int, y1: int, x2: int, y2: int,
             device: str | None, steps: int = 12) -> None:
        """Drag the absolute tablet pointer without involving the host."""
        x1 = max(0, min(x1, SCREEN_WIDTH))
        y1 = max(0, min(y1, SCREEN_HEIGHT))
        x2 = max(0, min(x2, SCREEN_WIDTH))
        y2 = max(0, min(y2, SCREEN_HEIGHT))

        def point(x: int, y: int) -> tuple[dict[str, Any], dict[str, Any]]:
            return {"type": "abs", "data": {
                "axis": "x", "value": round(x * 32767 / SCREEN_WIDTH),
            }}, {"type": "abs", "data": {
                "axis": "y", "value": round(y * 32767 / SCREEN_HEIGHT),
            }}

        start = list(point(x1, y1))
        start.append({"type": "btn", "data": {"button": "left", "down": True}})
        arguments: dict[str, Any] = {"events": start}
        if device:
            arguments["device"] = device
        self.command("input-send-event", arguments)
        for index in range(1, steps + 1):
            progress = index / steps
            events = list(point(round(x1 + (x2 - x1) * progress),
                               round(y1 + (y2 - y1) * progress)))
            arguments = {"events": events}
            if device:
                arguments["device"] = device
            self.command("input-send-event", arguments)
            time.sleep(0.03)
        release: dict[str, Any] = {
            "events": [{"type": "btn", "data": {"button": "left", "down": False}}]
        }
        if device:
            release["device"] = device
        self.command("input-send-event", release)

    def screenshot(self, path: str) -> None:
        output = Path(path).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        # QEMU's screendump command writes PPM regardless of the filename
        # suffix. Convert it to the requested artifact format so reports and
        # image viewers can consume a normal .png.
        ppm = output.with_name(output.name + ".qemu.ppm")
        self.command("screendump", {"filename": str(ppm)})
        if output.suffix.lower() != ".ppm":
            if not shutil.which("convert"):
                raise RuntimeError("screenshot conversion requires ImageMagick convert")
            subprocess.run(["convert", str(ppm), str(output)], check=True)
            ppm.unlink(missing_ok=True)
        else:
            ppm.replace(output)
        if not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError(f"QEMU did not create screenshot: {output}")

    def close(self) -> None:
        self.sock.close()


def run_step(qmp: Qmp, step: dict[str, Any], pointer_device: str | None,
             key_device: str | None) -> None:
    action = step.get("action")
    if action == "key":
        keys = step.get("keys")
        if not isinstance(keys, str):
            raise ValueError("key action requires string 'keys'")
        qmp.key(keys, key_device)
    elif action == "text":
        value = step.get("text")
        if not isinstance(value, str):
            raise ValueError("text action requires string 'text'")
        qmp.type_text(value, key_device)
    elif action == "click":
        x, y = step.get("x"), step.get("y")
        if not isinstance(x, int) or not isinstance(y, int):
            raise ValueError("click action requires integer x and y")
        qmp.click(x, y, pointer_device)
    elif action == "drag":
        coordinates = [step.get(name) for name in ("x1", "y1", "x2", "y2")]
        if any(not isinstance(value, int) for value in coordinates):
            raise ValueError("drag action requires integer x1, y1, x2, and y2")
        steps = step.get("steps", 12)
        if not isinstance(steps, int) or steps < 1:
            raise ValueError("drag steps must be a positive integer")
        qmp.drag(*coordinates, pointer_device, steps)
    elif action == "sleep":
        seconds = step.get("seconds", 0.2)
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or seconds < 0:
            raise ValueError("sleep seconds must be a non-negative number")
        time.sleep(seconds)
    elif action == "screenshot":
        path = step.get("path")
        if not isinstance(path, str) or not path:
            raise ValueError("screenshot action requires string 'path'")
        qmp.screenshot(path)
    elif action in {"activate", "focus"}:
        # Kept as a no-op so existing macro fixtures can be shared. A headless
        # QEMU instance has no host window to activate.
        return
    else:
        raise ValueError(f"unknown headless macro action: {action!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("macro", type=Path)
    parser.add_argument("--qmp", default=os.environ.get("ASPARTAME_QEMU_QMP", QMP_DEFAULT))
    parser.add_argument("--device", default=os.environ.get("ASPARTAME_QEMU_INPUT_DEVICE", ""),
                        help="optional QEMU input device name for pointer events")
    parser.add_argument("--key-device", default=os.environ.get("ASPARTAME_QEMU_KEY_DEVICE", ""),
                        help="optional QEMU input device name for keyboard events")
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat must be positive")
    try:
        payload = json.loads(args.macro.read_text())
        if not isinstance(payload, list) or not all(isinstance(step, dict) for step in payload):
            raise ValueError("macro root must be an array of objects")
        qmp = Qmp(args.qmp)
        try:
            for _ in range(args.repeat):
                for index, step in enumerate(payload):
                    try:
                        run_step(qmp, step, args.device or None, args.key_device or None)
                    except Exception as error:
                        raise RuntimeError(f"step {index} ({step.get('action')!r}) failed: {error}") from error
        finally:
            qmp.close()
    except (OSError, json.JSONDecodeError, ValueError, RuntimeError) as error:
        print(f"qemu-headless-macro: {error}")
        return 1
    print(f"qemu-headless-macro=PASS steps={len(payload)} repeats={args.repeat} qmp={args.qmp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
