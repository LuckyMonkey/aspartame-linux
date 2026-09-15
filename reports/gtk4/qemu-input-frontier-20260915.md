# GTK4 QEMU keyboard frontier — 2026-09-15

The original launcher exposed keyboard devices but QMP injection did not reach
the shell. The launcher now includes an explicit `virtio-keyboard-pci` device.
On a fresh boot, QMP `input-send-event` F1 reached the modern shell and opened
Neighborhood; F2, F3, F5, and F6 likewise switched to Group, Home, Journal,
and Frame. 1920×1080 screenshots are recorded in the accompanying input
evidence report.

This is narrower than the previous “no `/dev/input/event*`” description: the
guest devices exist, but the current QEMU injection path is not reaching them.
Semantic GTK4 key routing remains implemented and must be tested separately
once the transport is repaired. This report does not count physical-keyboard
parity as passed.

Physical Tab/Shift+Tab/Enter/Space/Escape and F4 Activity switching still need
separate evidence. This report does not claim the full physical-input gate.
