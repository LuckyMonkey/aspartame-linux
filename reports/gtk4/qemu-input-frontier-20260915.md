# GTK4 QEMU keyboard frontier — 2026-09-15

The live guest exposes keyboard devices (`event1` AT keyboard, `event3` QEMU
USB keyboard, and `event4` QEMU virtio keyboard). A root read probe was run on
each node while injecting `F1` through both `scripts/qemu-send-key.py` (QMP
`input-send-event`) and the QEMU monitor `sendkey f1` command. No evdev records
were emitted and the modern shell remained on Home; its shell log recorded no
new semantic F-key event.

This is narrower than the previous “no `/dev/input/event*`” description: the
guest devices exist, but the current QEMU injection path is not reaching them.
Semantic GTK4 key routing remains implemented and must be tested separately
once the transport is repaired. This report does not count physical-keyboard
parity as passed.
