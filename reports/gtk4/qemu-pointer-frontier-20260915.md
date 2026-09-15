# GTK4 QEMU pointer evidence — 2026-09-15

With the modern GTK4 Help Activity active, `scripts/qemu-send-pointer.py`
clicked the `Journal` expander at guest coordinate `(100, 320)`. The expander
opened in place and its Journal article text became visible in the subsequent
1920×1080 capture. This proves the QEMU absolute-tablet path reaches the real
GTK4 Activity surface and that pointer interaction is functional.

Evidence: `reports/screenshots/sugar-20260915-093715-v0.0.31.png` and OCR
sidecar. Keyboard injection remains separately unproven; see
`qemu-input-frontier-20260915.md`.
