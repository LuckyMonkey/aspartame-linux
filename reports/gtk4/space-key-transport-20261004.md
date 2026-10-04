# Headless F7/F8 Space transport — 2026-10-04

## Result

PASS. The newest standalone ISO accepts QMP keyboard events without mapping a
host QEMU window or grabbing the host mouse.

- ISO: `aspartame-2026.10.04-x86_64.iso`
- SHA-256: `742c849ac5bf55521a9e099a8234b0d1142451987fc5d379813e6807c1965cf7`
- QEMU: `QEMU_HEADLESS=1`, `QEMU_DISPLAY=none`, QMP socket
  `/tmp/aspartame-qemu-qmp-headless`, SSH port `2223`
- GTK3 shell PID: `762`
- GTK4 shell PID: `1174`

## Probe

From the host:

```sh
ASPARTAME_QEMU_QMP=/tmp/aspartame-qemu-qmp-headless \
  python3 scripts/qemu-send-key.py F7
```

Guest Space controller status immediately after F7:

```text
current=0
count=4
gtk3_pid=762
gtk4_pid=1174
keys=F7:GTK3,F8:GTK4
```

The same command with `F8` returned:

```text
current=1
count=4
gtk3_pid=762
gtk4_pid=1174
keys=F7:GTK3,F8:GTK4
```

The full macro also captured both states:

- [F7 Classic Space](qemu-f7-space.png)
- [F8 Modern Space](qemu-f8-space.png)

The two screenshots show complete single-surface Homes, not a split layout.
The packaged headless macro is `macros/qemu/headless-space-keys.json`.

This closes the physical GTK3/GTK4 Space-selection transport gate for the
supported headless QEMU path. The semantic Spaces primitive remains the
underlying action boundary; no history or split-screen behavior was added.
