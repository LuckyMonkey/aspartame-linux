# GTK4 Home catalog deduplication — 2026-09-19

## User-visible gap

The modern Home List previously displayed both the native GTK4 Calculate and
an unsupported classic Calculate bundle under the same display name. The
classic row was marked `Classic Space activity`, but the duplicate made the
modern catalog ambiguous.

## Fix

`jarabe.desktop.activitieslist._catalog_bundles()` now keeps classic entries
when no modern replacement exists. When a resolvable GTK4 bundle has the same
normalized Activity name, only the unsupported duplicate is hidden. This is a
catalog policy, not an Activity visual rewrite or a package uninstall.

## Evidence

- Guest rebuilt successfully after the change.
- Modern Space restarted as GTK4 PID `48013`.
- `org.laptop.Shell.ShowList` returned successfully.
- Screenshot: `reports/screenshots/sugar-20260919-125822-v0.0.31.png`
- SHA-256: `e52c0bc0aff1198ebf35b1154f6b4857d07773fca431c5a8c99b790bf3e47b9d`.
- Home reports `51 installed activities`.
- Native Calculate appears once with its GTK4 icon and `Stopped` state.
- Other classic-only entries remain explicitly available as Classic Space
  activities.

The Activity launch task ledger remains the authority for per-Activity parity;
this change only removes a shared shell catalog ambiguity.
