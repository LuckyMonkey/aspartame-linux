# GTK4 parity ledger — 2026-09-14

## Closed gap

GTK4 Frame exposes a stable accessible `Frame` label and `GROUP` role. The
current-source patch sequence handles historical hunk drift without hiding
runtime failures.

## Current evidence

- Guest preview build passes beyond patch 0015.
- GTK4 runtime check passes on desktop 1 (`pid=183604`).
- GTK3 runtime check passes on desktop 0 (`pid=33761`).
- The modern Space is restored after the comparison and passes again.
- Full host suite: 162 tests passed (`pytest -q`, 2026-09-14).
- Fresh guest lifecycle probe (2026-09-14): GTK4 Count launched/stopped for
  three consecutive cycles (PIDs `222220`, `222242`, `222263`), each reporting
  `cleanup=PASS`; final result `lifecycle-probe=PASS`.
- Fresh guest rebuild (2026-09-14): all preview patches applied or semantically
  verified through 0123, including 0015; toolkit import, Casilda 1.0,
  sugar-ext, Jarabe, and datastore metadata checks all passed.
- Native Calculate Activity (2026-09-14): staged into the rebuilt GTK4
  registry, launched through Journal (`org.aspartame.Calculate`), exposed its
  private `WAYLAND_SOCKET`, passed the GTK4 runtime check, and stopped cleanly.
- Calculate repeated lifecycle (2026-09-14): three live launch/stop cycles
  passed with PIDs `231101`, `231124`, and `231145`; every cycle reported
  `cleanup=PASS` and the probe ended `lifecycle-probe=PASS`.
- Image Viewer (2026-09-14): the pinned GTK4 source was staged, launched
  through Journal (`org.laptop.ImageViewerActivity`, PID `233782`), and stopped
  cleanly with the shell reporting the expected successful StopActivity call.
- Image Viewer repeated lifecycle (2026-09-14): three live launch/stop cycles
  passed with PIDs `246325`, `246348`, and `246369`; each reported
  `cleanup=PASS` and the probe ended `lifecycle-probe=PASS`.
- Terminal (2026-09-14): installed the guest `vte4` package after repairing
  pacman trust, rebuilt the GTK4 prefix, launched `org.laptop.Terminal` (PID
  `249258`) through Journal, and stopped it cleanly (`terminal-stop=PASS`).
- Terminal repeated lifecycle (2026-09-14): three standard launch/stop cycles
  passed with PIDs `249309`, `249331`, and `249352`; all reported
  `cleanup=PASS` and the probe ended `lifecycle-probe=PASS`.
- Browse (2026-09-14): installed guest `webkitgtk-6.0`, staged the pinned GTK4
  source, and passed three Journal launch/stop cycles with PIDs `252075`,
  `252096`, and `252117`; every cycle reported `cleanup=PASS`.
- The guest build now explicitly gates `vte-2.91-gtk4 >= 0.84` and
  `webkitgtk-6.0 >= 2.50`; both checks pass in the current VM build.
- Full modern Activity matrix (2026-09-14): Help, Count, Calculate, Image
  Viewer, Terminal, Browse, and Log each completed a live Journal launch/stop
  cycle with `cleanup=PASS`; final result `activity-matrix=PASS` (PIDs
  `254754`, `254786`, `254816`, `254846`, `254876`, `254906`, `254937`).
- Consolidated guest checker (2026-09-14): GTK4/PyGObject import, toolkit suite
  (`55 passed`), sugar-ext configuration, shell GTK4 configure gate, and
  preview shell boot all passed. The checker still intentionally does not claim
  the full replacement gate.

## Ranked remaining gaps

1. Physical F1–F6 delivery remains below the QEMU/evdev transport. Semantic
   `ShowHome`, `ShowJournal`, `ShowFrame`, `ShowNeighborhood`, `ShowGroup`, and
   `ShowControlPanel` actions are reliable, so no additional keybinding layer
   is justified until keyboard events reach the guest device.
   A direct QMP `F8` injection after `sugar-gtk4-space.sh setup` left the guest
   on workspace 0, confirming this remains an input-delivery issue rather than
   a missing semantic action.
2. Neighborhood/Group peer actions need a real collaboration peer. The empty
   state and accessible roots are verified; inventing peers would not prove
   Sugar collaboration behavior.
3. More individual Activities still require GTK4 ports. Browse, Terminal,
   Image Viewer, Calculate, Count, Help, and Log now provide verified modern
   Activity paths; remaining legacy bundles need separate ports.

## Complexity policy

No new Spaces, launcher, datastore, or input abstraction is introduced by the
Frame fix. GTK3 remains a separate process and behavioral reference.
