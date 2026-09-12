#!/usr/bin/env python3
"""Inject a key through QEMU QMP for deterministic guest-input tests."""

import json
import socket
import sys
import time

KEYCODES = {f"F{i}": 58 + i for i in range(1, 13)}


def command(sock, name, arguments=None):
    payload = {"execute": name}
    if arguments:
        payload["arguments"] = arguments
    sock.sendall((json.dumps(payload) + "\r\n").encode())
    while True:
        response = json.loads(sock.makefile().readline())
        if "return" in response:
            return response
        if "error" in response:
            raise RuntimeError(response["error"])


def main():
    key = sys.argv[1].upper() if len(sys.argv) == 2 else ""
    if key not in KEYCODES:
        raise SystemExit(f"usage: {sys.argv[0]} F1..F12")
    code = KEYCODES[key]
    with socket.socket(socket.AF_UNIX) as sock:
        sock.connect("/tmp/aspartame-qemu-qmp")
        sock.recv(4096)
        command(sock, "qmp_capabilities")
        for down in (True, False):
            command(sock, "input-send-event", {
                "events": [{"type": "key", "data": {
                    "down": down, "key": {"type": "number", "data": code}
                }}]
            })
            time.sleep(0.05)


if __name__ == "__main__":
    main()
