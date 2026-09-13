#!/usr/bin/env python3
"""Inject a key through QEMU's QMP USB keyboard for guest-input tests."""

import json
import socket
import sys

KEYCODES = {f"F{i}": f"f{i}" for i in range(1, 13)}
KEYCODES.update({letter: letter.lower() for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"})
KEYCODES.update({"TAB": "tab", "ENTER": "ret", "RETURN": "ret",
                 "ESC": "esc", "ESCAPE": "esc", "SPACE": "spc",
                 "BACKSPACE": "backspace"})
SOCKET = "/tmp/aspartame-qemu-qmp"


def _reply(sock):
    data = b""
    while b"\n" not in data:
        data += sock.recv(4096)
    line, _, _ = data.partition(b"\n")
    return json.loads(line.decode())


def _command(sock, events):
    sock.sendall((json.dumps({
        "execute": "input-send-event",
        "arguments": {"events": events},
    }) + "\n").encode())
    reply = _reply(sock)
    if "error" in reply:
        raise RuntimeError(reply["error"]["desc"])


def main():
    key = sys.argv[1].upper() if len(sys.argv) == 2 else ""
    if key not in KEYCODES:
        raise SystemExit(f"usage: {sys.argv[0]} F1..F12 or A..Z; TAB, ENTER, ESC, SPACE")
    with socket.socket(socket.AF_UNIX) as sock:
        sock.settimeout(2)
        sock.connect(SOCKET)
        _reply(sock)
        sock.sendall(b'{"execute":"qmp_capabilities"}\n')
        _reply(sock)
        qcode = KEYCODES[key]
        _command(sock, [{"type": "key", "data": {"down": True,
                                                   "key": {"type": "qcode", "data": qcode}}}])
        _command(sock, [{"type": "key", "data": {"down": False,
                                                   "key": {"type": "qcode", "data": qcode}}}])


if __name__ == "__main__":
    main()
