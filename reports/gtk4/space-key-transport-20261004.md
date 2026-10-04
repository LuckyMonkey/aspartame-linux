# Headless F7/F8 Space transport — 2026-10-04

## Result

PASS. The newest standalone ISO accepts QMP keyboard events without mapping a
host QEMU window or grabbing the host mouse.

- ISO: `aspartame-2026.10.04-x86_64.iso`
- SHA-256: `0ba689624f6418e0cb0c5c5d1a3b064174640dbadc13a25fbe3e06c87b602363`
- QEMU: `QEMU_HEADLESS=1`, `QEMU_DISPLAY=none`, QMP socket
  `/tmp/aspartame-qemu-qmp-chirality-packaged`, SSH port `2228`
- GTK3 shell PID: `834`
- GTK4 shell PID: `1291`

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

The full macro also captured both states and repeated the round trip three
times:

- [F7 Classic Space](qemu-f7-space.png)
- [F8 Modern Space](qemu-f8-space.png)

The two screenshots show complete single-surface Homes, not a split layout.
The packaged headless macro is `macros/qemu/headless-space-keys.json`; the
qualification run also used the checked-in runner with an equivalent four-step
F7/sleep/F8/sleep sequence and `--repeat 3`.

This closes the physical GTK3/GTK4 Space-selection transport gate for the
supported headless QEMU path. The semantic Spaces primitive remains the
underlying action boundary; no history or split-screen behavior was added.
The remaining QEMU input frontier is F1–F6 navigation/Activity semantics,
which is tracked separately from Space selection.
