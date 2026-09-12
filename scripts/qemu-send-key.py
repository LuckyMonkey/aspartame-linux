#!/usr/bin/env python3
"""Inject a function key through QEMU's monitor for guest-input tests."""

import socket
import sys

KEYCODES = {f"F{i}": f"f{i}" for i in range(1, 13)}


def main():
    key = sys.argv[1].upper() if len(sys.argv) == 2 else ""
    if key not in KEYCODES:
        raise SystemExit(f"usage: {sys.argv[0]} F1..F12")
    # HMP's symbolic sendkey path targets QEMU's configured keyboard device.
    # QMP input-send-event accepts the command but, on some QEMU versions,
    # does not route it to the USB keyboard exposed to the guest.
    with socket.socket(socket.AF_UNIX) as sock:
        sock.settimeout(2)
        sock.connect("/tmp/aspartame-qemu-monitor")
        sock.recv(4096)
        # Explicit hold time prevents a stuck key/repeat storm in QEMU's HMP
        # backend while still producing a normal press/release pair.
        sock.sendall((f"sendkey {KEYCODES[key]} 100\n").encode())
        # Wait for the monitor prompt: closing immediately after the command
        # can interrupt QEMU's delayed key-release timer.
        response = b""
        while b"(qemu)" not in response:
            response += sock.recv(4096)


if __name__ == "__main__":
    main()
