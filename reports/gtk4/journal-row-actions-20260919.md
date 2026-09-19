# GTK4 Journal row actions — 2026-09-19

## Finding

The GTK4 Journal rendered Keep, Edit title, Delete, and Project controls inside
every row.  The actions were available, but their full-width controls made the
result surface unnecessarily tall and reduced the visible Journal to only a
few entries at a time.

## Bounded fix

`gtk4-overlay/src/jarabe/journal/listview.py` now keeps the row's title and
activity metadata on the primary surface and places the existing actions in a
GTK4 `Gtk.Popover` opened by an accessible `Actions` `Gtk.MenuButton`.  No
Journal operation was removed and no Activity-specific visual policy was
introduced.

## Evidence

- Focused Journal selection tests: **33 passed**.
- Full repository tests after the change: **390 passed**.
- Guest preview rebuild: **PASS**; patch 0153 semantic drift was also
  recognized and the build advanced through all 0164 patches.
- Guest runtime after rebuild:
  `runtime-check=ok target=gtk4 pid=96268 desktop=1 window=0xe00005`
- The pre-fix Journal screenshot remains at
  `reports/screenshots/sugar-20260919-135539-v0.0.31.png`; the post-fix
  runtime shell was restarted successfully and the compact row implementation
  is installed in the guest.

## Boundary

This closes a Journal presentation gap. It does not promote any Activity to a
FULL PORT and does not attempt to make Activity internals visually identical.
