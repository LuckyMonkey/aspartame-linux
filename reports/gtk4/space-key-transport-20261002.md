# Space-selection key transport — 2026-10-02

This is a transport qualification record for the rebuilt standalone image,
not a claim about the Sugar key handler.

## Image and setup

- ISO: `aspartame-2026.10.02-x86_64.iso`
- SHA-256: `c7112675cbe69b9a79eee7343f7956d4cef2c8415ac34fd88d09f8cb47fc64f2`
- Guest input node: `QEMU QEMU USB Keyboard` (`/dev/input/event3`)
- Controller: `/usr/lib/aspartame/gtk4-preview/scripts/sugar-gtk4-space.sh`

## Probe

With the desktop running in the comparison session, a reader captured
`/dev/input/event3` for three seconds while the host QMP helper injected one
F10 press and release:

```sh
timeout 3 od -An -tx1 /dev/input/event3
python3 scripts/qemu-send-key.py F10
```

The QMP command returned success, but the evdev capture produced no bytes on
either the USB keyboard (`event3`) or virtio keyboard (`event4`). Repeating
the check with QMP `send-key` and the HMP `sendkey` command produced the same
result. The guest was running, so this is a QEMU input-delivery boundary, not
a GTK3 key grabber or GTK4 shell-action failure.

The host-side synthetic `xdotool` check also cannot stand in for a physical
keyboard check: with `grab-on-hover=on`, the pointer grab blocks the automated
move path. A human must still verify F7/F8 with the pointer hovering over the
QEMU window. The reliable, testable path remains the semantic Spaces button
and controller actions below.

The launcher now gives the display a stable `video0` ID and binds the USB and
virtio keyboard devices to that display. QEMU's live device tree confirmed
those routes, but a repeat of the F10 capture still produced zero bytes on
both guest keyboard nodes. The explicit routing is retained as deterministic
configuration for future transport work; it is not counted as a physical-key
pass.

## Latest rerun

On the same live QEMU configuration, the QMP helper reached the virtio
keyboard path:

```text
/dev/input/event3 QEMU QEMU USB Keyboard: 0 bytes
/dev/input/event4 QEMU Virtio Keyboard: 192 bytes for the paired F7/F8 run
F7-only event4 capture: 96 bytes, EV_KEY code 65
F8-only event4 capture: 96 bytes, EV_KEY code 66
```

The X server has both event3 and event4 registered as libinput keyboards.
Despite the delivered F7/F8 key events, `_NET_CURRENT_DESKTOP` remained `1`
after individual F7 and F8 injections, so the Space action still did not
complete through this QMP path. The semantic controller and Spaces button do
complete the same transition and remain the reliable user/test path.

## Reliable path

The packaged semantic actions and side-by-side action remain passing:

```sh
sugar-gtk4-space.sh gtk3
sugar-gtk4-space.sh gtk4
sugar-gtk4-space.sh side-by-side
```

Those actions are the current button/automation path while physical F7/F8
transport remains open.
