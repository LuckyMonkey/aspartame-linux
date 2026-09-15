# GTK4 Frame runtime verification — 2026-09-15

The live GTK4 shell service `ShowFrame()` returned `1` and revealed the Sugar
Frame at 1920×1080. The capture shows the top activity/device strip, edge
navigation arrows, owner icon, and bottom system controls rendered inside the
fullscreen GTK4 shell surface.

Evidence: `reports/screenshots/sugar-20260915-075309-v0.0.31.png` and OCR
sidecar. No separate native top-level window was introduced.
