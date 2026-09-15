# GTK4 semantic zoom service verification — 2026-09-15

Applied `0128-service-dedupe-zoom-actions.patch` to the live GTK4 source. The
service now contains one authoritative `ShowNeighborhood()` and one
`ShowGroup()` implementation; both close an open Control Panel before changing
the zoom level. A subsequent `ShowGroup()` call returned `1` and rendered the
Group surface at 1920×1080.

Evidence: `reports/screenshots/sugar-20260915-075234-v0.0.31.png` and OCR
sidecar. The first `ShowControlPanel()` returned `0` because an existing modal
panel was already present; this is expected modal-state protection.
