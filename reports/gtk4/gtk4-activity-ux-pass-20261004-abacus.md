# GTK4 Abacus UX qualification

Date: 2026-10-04

## Result

Abacus now presents its five place-value rods as a centered, bounded card at
1920x1080. Each row keeps the place label, decrement button, bead rail, and
increment button together. The previous layout allowed expanding rows and an
expanding bead label to push the controls to opposite screen edges and leave
the activity looking like a sparse table.

The focused headless development-guest visual sweep passed:

```text
visual-sweep=COMPLETE pass=1 fail=0 resolution=1920x1080
```

The updated screenshot is stored in the development share at
`reports/gtk4/abacus-ux-20261004/com.homegrownapps.abacus.png`.

The seeded Journal resume and cleanup probe also passed:

```text
cycle=1 ... resume=PASS service-release=PASS shell-cleanup=PASS
abacus-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

## Changes

- Removed vertical expansion from the rod card and its rows.
- Replaced the full-width row boxes with centered GTK4 grids.
- Added readable place names, an instruction line, and meaningful accessible
  names for all increment/decrement and clear actions.
- Kept the existing five-rod value model and JSON Journal payload unchanged.

This is development-guest evidence; the GTK3 Activity remains installed as a
fallback/reference until the broader retirement gates are met.
