# QEMU GTK4 function-key evidence — 2026-09-15

After adding `-device virtio-keyboard-pci` to `scripts/run-qemu.sh`, the fresh
live VM accepted QMP keyboard events through `scripts/qemu-send-key.py`.

| Key | Observed GTK4 result | Screenshot |
|---|---|---|
| F1 | Neighborhood, including “Scan network” | `sugar-20260915-101000-v0.0.31.png` |
| F2 | Group/owner view | `sugar-20260915-101002-v0.0.31.png` |
| F3 | Home | `sugar-20260915-101005-v0.0.31.png` |
| F5 | Journal entries | `sugar-20260915-101007-v0.0.31.png` |
| F6 | Frame overlay | `sugar-20260915-101008-v0.0.31.png` |
| F4 | Active Count Activity surface | `sugar-20260915-101245-v0.0.31.png` |

Each event was injected into the running QEMU instance and followed by a
1920×1080 capture. Tab/Shift+Tab/Enter/Space/Escape remain separate semantic
focus/input checks; the screenshots here establish physical function-key
delivery and shell view transitions only.

An additional F5 → Escape attempt left Journal visible, so physical Escape is
currently **not passed**. The failure is retained as a concrete follow-up rather
than being inferred from the successful F-key transport.
