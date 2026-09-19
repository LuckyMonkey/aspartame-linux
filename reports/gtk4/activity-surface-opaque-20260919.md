# Casilda Activity surface boundary — 2026-09-19

## Result

The GTK4 shell's Casilda page now has an explicit opaque black background.
This removes the short white allocation stripe that appeared between the Sugar
top bar and a newly mapped Activity surface. The change is shell-owned and
does not alter an Activity's internal visual design.

## Runtime evidence

- Guest rebuilt with patch `0159-shell-opaque-activity-surface.patch`.
- Modern Space restarted from the rebuilt tree: GTK4 PID `44019`.
- Help launched through the real Journal D-Bus path; `help-visible=PASS` and
  `help-search=PASS`, Activity PID `44522`.
- Screenshot: `reports/screenshots/sugar-20260919-125340-v0.0.31.png`
- Screenshot resolution: 1920×1080.
- Screenshot SHA-256: `ccfa5ec1d207b8b9ce03c7fcdd884a0179e8b62ea081cabd3549242fe0b0eca9`.
- Visual check: no white stripe or separate launch-surface chrome remains at
  the top edge of the black Help canvas.

## Verification boundary

This proves the shared shell/Casilda allocation boundary for Help. It does not
claim visual parity for every Activity; per-Activity work remains in the launch
task ledger.
