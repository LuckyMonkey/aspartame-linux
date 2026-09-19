# GTK4 Settings full-monitor coverage — 2026-09-19

## Finding

The Control Panel window requested monitor dimensions minus two Sugar grid-cell
margins.  Under the guest window manager that left Home chrome and white
margins visible around the black Settings surface.

## Fix

Preview patch 0167 changes the Control Panel geometry request to the complete
monitor width and height.  The Sugar top bar remains visible as the shell's
canonical chrome; the Settings content now owns the entire area beneath it.

## Evidence

- Guest preview rebuild: **PASS**, including patch 0167.
- Runtime check after a clean modern-Space restart:
  `runtime-check=ok target=gtk4 pid=108601 desktop=1 window=0xe00005`
- D-Bus `ShowControlPanel` returned `true`.
- Screenshot: `reports/screenshots/sugar-20260919-140510-v0.0.31.png`
  (1920×1080). It shows a full black Settings surface, Sugar top bar,
  Settings search, stop control, and the complete section grid without the
  previous white side/bottom margins or Home toolbar duplication.

This is shell window coverage, not a claim that every settings section has
GTK4 feature parity beyond the documented W10 checks.
