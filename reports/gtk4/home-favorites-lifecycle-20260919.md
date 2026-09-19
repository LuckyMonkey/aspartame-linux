# Home Favorites lifecycle evidence — 2026-09-19

## Scope

This check covers the shell-owned lifecycle boundary only. It does not promote
Help or any other Activity to a full visual port; Activity-specific artwork and
toolbar work remains in `docs/sugar-modernization/ACTIVITY_LAUNCH_TASKS.md`.

## Evidence

- Guest rebuild passed through preview patch `0168` and repaired the stale
  Favorites source semantically.
- `python3 -m pytest -q` — **395 passed**.
- `sugar-gtk4-runtime-check.sh gtk4` — **PASS**, modern PID `125913`,
  GTK3 reference PID `129151`, workspace `1`.
- Help launch produced activity `7d5cdc5604ef4079b60eaafec16c589f`.
- `org.laptop.Shell.StopActivity` returned `true`; no `helpactivity4` process
  remained after the stop request.
- Post-stop Home capture: [`sugar-20260919-142609-v0.0.31.png`](../../reports/screenshots/sugar-20260919-142609-v0.0.31.png)
  (1920×1080).

## Result

The process and shell return path are clean. The Favorites ring now subscribes
to the authoritative Activity Presentation model instead of treating the last
Journal color as proof that an Activity is running. The remaining yellow Help
question-mark artwork in the capture is recorded as an Activity/icon task, not
silently treated as a completed shell-state result; it is therefore deferred
to the Help row's `ICON`/`CHROME` work rather than triggering a global visual
normalization pass.
