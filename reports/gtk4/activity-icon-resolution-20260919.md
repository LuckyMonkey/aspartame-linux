# GTK4 Activity icon resolution — 2026-09-19

## Scope

This pass addressed the shared shell boundary behind missing Activity icons. It
did not alter Activity-internal artwork or attempt to make Activities visually
identical.

## Change

`jarabe.desktop.activitieslist` now resolves an Activity icon from either an
absolute metadata path or a bundle-relative basename. Home rows and Activity
palettes use the same resolver. If metadata points at no file, the shell emits
a warning and displays the Sugar `activity-start` icon instead of leaving an
empty widget.

## Verification

- Host package inventory: 48 shipped GTK4 package icons found; 48/48 are valid
  SVG files.
- `python3 -m py_compile gtk4-overlay/src/jarabe/desktop/activitieslist.py`:
  PASS.
- `make test`: **388 passed**.
- Guest development sync: PASS.
- Full guest GTK4 rebuild: PASS (`datastore metadata reader: PASS`; GTK4
  toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS).

## Boundary

This proves metadata resolution and fallback behavior. It does not claim that
every Activity's internal toolbar, artwork, or feature set matches its GTK3
reference. Those remain in the per-Activity queue in
`docs/sugar-modernization/ACTIVITY_LAUNCH_TASKS.md`.
