#!/usr/bin/env python3
"""Send one absolute USB-tablet click through the QEMU monitor."""

import json
import socket
import sys


SOCKET = "/tmp/aspartame-qemu-qmp"


def _reply(sock):
    data = b""
    while b'"return"' not in data and b'"error"' not in data:
        data += sock.recv(4096)
    return json.loads(data.decode())


def _command(sock, events):
    sock.sendall((json.dumps({
        "execute": "input-send-event",
        "arguments": {"events": events},
    }) + "\n").encode())
    reply = _reply(sock)
    if "error" in reply:
        raise RuntimeError(reply["error"]["desc"])


def main():
    if len(sys.argv) != 3:
        raise SystemExit(f"usage: {sys.argv[0]} X Y (guest pixels at 1920x1080)")
    x, y = (max(0, min(int(value), 1920 if i == 0 else 1080))
            for i, value in enumerate(sys.argv[1:]))
    scale_x, scale_y = 32767 / 1920, 32767 / 1080
    with socket.socket(socket.AF_UNIX) as sock:
        sock.connect(SOCKET)
        _reply(sock)
        sock.sendall(b'{"execute":"qmp_capabilities"}\n')
        _reply(sock)
        _command(sock, [
            {"type": "abs", "data": {"axis": "x", "value": round(x * scale_x)}},
            {"type": "abs", "data": {"axis": "y", "value": round(y * scale_y)}},
            {"type": "btn", "data": {"button": "left", "down": True}},
        ])
        _command(sock, [{"type": "btn", "data": {"button": "left", "down": False}}])


if __name__ == "__main__":
    main()
