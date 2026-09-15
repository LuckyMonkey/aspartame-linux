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

An F5 → Escape sequence first dismissed the pointer-opened palette; a second
Escape cancelled an active Journal title edit and returned the row to its normal
presentation. Journal detail Escape remains a separate navigation check.

After adding the shell-level Escape shortcut, a live F6 → Escape sequence
closed the revealed Frame and returned to Home. Evidence:
`sugar-20260915-101954-v0.0.31.png`.

From Journal, physical Enter activated the selected Clock entry and produced a
live Clock Activity surface (`sugar-20260915-101822-v0.0.31.png`).
