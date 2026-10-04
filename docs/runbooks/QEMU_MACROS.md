# QEMU visual-test macros

`scripts/qemu-headless-macro.py` is the default visual-test driver. It talks to
QEMU's QMP socket and never maps, activates, or clicks a host window. Keyboard
events use QEMU's monitor, pointer events use the absolute USB tablet, and
screenshots use QEMU's framebuffer `screendump` command.

Start the VM without a host display:

```sh
QEMU_HEADLESS=1 QEMU_QMP=/tmp/aspartame-qemu-qmp-headless \
  QEMU_SNAPSHOT=1 SSH_FORWARD_PORT=2223 ./scripts/run-qemu.sh
```

`QEMU_SNAPSHOT=1` lets an automated qualification VM read the normal test
disks without writing to or locking in test state. Use a separate SSH port and
QMP socket when an interactive VM is already running.

Create a JSON macro:

```json
[
  {"action": "activate"},
  {"action": "key", "keys": "F8"},
  {"action": "sleep", "seconds": 1},
  {"action": "click", "x": 640, "y": 420},
  {"action": "screenshot", "path": "reports/screenshots/qemu-space.png"}
]
```

Run it from the project root:

```sh
ASPARTAME_QEMU_QMP=/tmp/aspartame-qemu-qmp-headless \
  ./scripts/qemu-headless-macro.py /path/to/macro.json
```

Supported actions are `key`, `text`, `click`, `sleep`, and `screenshot`;
`activate` is accepted as a no-op for shared fixtures. Click coordinates are
guest pixels in the 1920×1080 virtual display. The runner does not invoke a
shell, so typed text and coordinates stay data rather than becoming commands.
Button press and release are sent as separate QMP commands; the deterministic
Calculate `7+8=15` macro qualifies semantic pointer activation. Use
`--repeat N` for a deterministic stress loop. The older `scripts/qemu-macro.py`
remains an explicitly interactive X11 helper and should not be used during
normal desktop work.

QMP framebuffer capture and absolute pointer activation are qualified. A
macro reporting `PASS` still means only that its transport steps completed
unless the macro has a semantic assertion or a paired guest-side probe. The
Spaces button/AT-SPI probe and the guest controller qualify side-by-side
comparison without host focus. The probe also checks both managed windows with
`sugar-x11-workspace.py inspect`: both must be on workspace 0, GTK3 must
occupy the left half, and GTK4 must occupy the right half at full display
height. The checked-in `spaces-side-by-side.json` macro only captures the
already-qualified framebuffer; it does not pretend that F7/F8 transport passed.

Run the complete headless qualification against a running VM with:

```sh
SSH_PORT=2223 ASPARTAME_QEMU_QMP=/tmp/aspartame-qemu-qmp-headless \
  ./scripts/qualify-qemu-spaces-side-by-side.sh
```

Physical F7/F8 remains a separate open input transport check; the current
QEMU key macro reaches X11 but does not complete the workspace transition.
