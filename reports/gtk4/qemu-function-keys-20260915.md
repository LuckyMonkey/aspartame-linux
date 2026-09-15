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

Each event was injected into the running QEMU instance and followed by a
1920×1080 capture. F4 requires an active Activity to prove Activity view
switching; Tab/Shift+Tab/Enter/Space/Escape remain separate input checks.
