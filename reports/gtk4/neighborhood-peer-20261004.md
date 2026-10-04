# GTK4 Neighborhood peer qualification — 2026-10-04

## Result

PASS for the packaged GTK4 Neighborhood surface with two headless QEMU
guests. The test used the newly rebuilt ISO and did not use a development
share or host pointer input.

## Build under test

- ISO: `aspartame-2026.10.04-x86_64.iso`
- ISO SHA-256: `cd482df31abf4d249bba2e55b211610061fa79c10d75c0d5cd0ed5eeda447016`
- GTK4 runtime SHA-256: `d3fc7b68142d94031ad6ed427243654ad3d49faab3c16622c0d70e1c32d28b1e`
- Runtime: `/usr/lib/aspartame/gtk4-preview`
- Both guests booted the packaged runtime with `QEMU_DEV_SHARE_MOUNT=0`.

## Qualification evidence

- GTK4 shell process remained alive on both guests after clean boot.
- Latest GTK4 shell logs contained no `Traceback`, `NameError`,
  `AttributeError`, `TypeError`, or `favoriteslayout` fatal markers.
- `sugar-gtk4-runtime-check.sh gtk4` passed on both guests; both modern
  surfaces were active on workspace 1.
- `ShowNeighborhood()` returned `boolean true` on both private GTK4 D-Bus
  session buses.
- The ATSPI probe passed on both guests and found a `Neighborhood` grouping
  under the GTK4 `Sugar` frame.
- The private QEMU link used static `10.77.0.1/24` and `10.77.0.2/24`
  addresses and distinct secondary-NIC MACs. Five-packet ping passed in both
  directions with 0% loss.
- Avahi/Salut discovery passed in both directions. Records included
  `arch-peer-a.local` at `10.77.0.1` and `arch-peer-b.local` at `10.77.0.2`,
  with distinct peer JIDs and `status=avail`.
- Headless QMP macros passed for both guests. The captured surfaces are:
  - [`qemu-peer-neighborhood-a.png`](qemu-peer-neighborhood-a.png)
  - [`qemu-peer-neighborhood-b.png`](qemu-peer-neighborhood-b.png)
- Both captures show the Neighborhood search header and three XO presence
  icons. The obsolete “No people or shared Activities are nearby yet.” label
  is absent when peer content exists.

## Repairs validated

- `0172` prevents `FavoritesLayout` from hashing `None` positioning data.
- `0173` removes duplicate shell navigation method definitions.
- `0174` makes the Neighborhood empty state follow actual buddy/activity
  content.
- `0175` moves Favorites accessibility setup to `ActivityIcon` and initializes
  its presentation model before refresh callbacks, fixing the clean-boot
  `NameError` and `AttributeError` regressions.

## Scope limits

This proves peer presence and Neighborhood rendering. It does not claim that
an Activity has been joined or shared between the two guests. The GTK3 shell
remains available on workspace 0 until the broader parity gates are complete.

The normal visual cadence, no-history behavior, and unrelated RNG streams are
unchanged; this qualification only exercises the GTK4 shell and its peer
presence path.
