# GTK4 parity ledger — 2026-09-14

## Closed gap

GTK4 Frame exposes a stable accessible `Frame` label and `GROUP` role. The
current-source patch sequence handles historical hunk drift without hiding
runtime failures.

The Mancala port also received a follow-up correctness fix: circular sowing
positions now map to valid pit indices, preventing an out-of-range crash while
distributing stones.

Native Reversi was added as another GTK4 Activity path; its legal-move and
capture model is local to the Activity and uses the existing lifecycle boundary.

Repeated lifecycle evidence (2026-09-14): Mastermind, Poll, Mancala, and
Reversi each completed three launch/stop cycles with `cleanup=PASS` (PIDs
`289078`–`289338`), confirming the newer ports do not leave stale processes or
Casilda surfaces.

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
- Post-profile Activity matrix rerun (2026-09-14): all seven registered modern
  bundles again completed Journal launch/stop with `cleanup=PASS`; final
  `activity-matrix=PASS` (PIDs `255598`, `255629`, `255660`, `255690`,
  `255720`, `255750`, `255780`).
- Activity catalog inventory (2026-09-14): the review inventory now contains
  84 unique legacy Fructose/Sugarizer rows (23 native Sugar bundles and 61
  Sugarizer web bundles); this closes the accounting gap without implying that
  those remaining bundles are already GTK4-ported.
- Current guest runtime recheck (2026-09-14): GTK4 remains healthy on desktop 1
  (`pid=230719`, `window=0x2a00005`); GTK3 remains available as the separate
  desktop-0 reference (`pid=33761`).
- Regression recheck (2026-09-14): host suite is now 168 passed; the guest
  GTK4 toolkit suite remains 55 passed, with the shell configure and preview
  boot gates passing.
- Fresh live Activity matrix (2026-09-14): Help, Count, Calculate, Image
  Viewer, Terminal, Browse, and Log each launched through Journal and stopped
  with immediate `cleanup=PASS` (PIDs `256080`, `256111`, `256141`, `256171`,
  `256201`, `256231`, `256261`); final result `activity-matrix=PASS`.
- Post-cleanup guest rebuild (2026-09-14): the GTK4 preview rebuilt beyond
  patch 0015, restarted successfully as PID `259457`, and its fresh startup
  log contains zero dangling `No bundle in` registry errors. The full Activity
  matrix still passes after the rebuild (PIDs `259165`–`259348`).
- Native Clock Activity (2026-09-14): added a live time/date GTK4 Activity,
  staged it as the original `tv.alterna.Clock` bundle, and verified Journal launch/stop cleanup
  in the full matrix (PID `262387`).
- Native JAMClock replacement (2026-09-14): replaced the legacy GTK3/Pygame
  entrypoint for `org.laptop.JAMClock` with a native GTK4 time/date Activity;
  guest rebuild and the expanded nine-Activity matrix passed launch/stop
  cleanup (PID `265219`).
- Isolated Home registry path (2026-09-14): the modern launcher now exposes
  all nine verified GTK4 bundles through `SUGAR_ACTIVITIES_PATH`, preventing
  GTK3 duplicates from winning Home lookup. After a clean GTK4 restart
  (`pid=265471`), the complete matrix passed again (final Log PID `266035`).
- Activity artwork validation (2026-09-14): added bundle-local Sugar SVG icons
  for Clock and JAMClock; both convert successfully with `rsvg-convert`, and
  the guest rebuild stages them without warnings.
- Host regression recheck after the Activity additions (2026-09-14): `pytest
  -q` passed 172 tests with the worktree clean.
- Help documentation refresh (2026-09-14): added a native Help topic covering
  Clock and JAMClock behavior; the guest rebuild passed and a live Help launch
  and stop cycle completed with `cleanup=PASS` (PID `271187`).
- Final current-state recheck (2026-09-14): host suite passed 172 tests;
  GTK4 runtime remained healthy (`pid=265471`, desktop 1), and the expanded
  nine-Activity matrix completed with `activity-matrix=PASS` (latest Log PID
  `271525`).
- Semantic Spaces round-trip (2026-09-14): `sugar-gtk4-space.sh gtk3` and
  `gtk4` switched deterministically between EWMH workspaces 0 and 1 while
  retaining the same GTK3 (`33761`) and GTK4 (`265471`) process identities.
- Home keyboard activation (2026-09-14): focused GTK4 Activity rows now
  activate on Enter, keypad Enter, or Space in addition to pointer/list
  activation; the guest preview rebuild passed with the updated overlay.
- Help surface documentation (2026-09-14): added Terminal/Browse usage and a
  Casilda private-surface explanation; the synchronized Help bundle completed
  a live launch/stop cycle with `cleanup=PASS` (PID `274364`).
- Clock identity correction (2026-09-14): the native Clock bundle now uses its
  original `tv.alterna.Clock` ID, preventing a duplicate unsupported GTK3 Clock
  entry. Guest rebuild and direct Journal lifecycle passed (`PID 277004`).
- Expanded matrix recheck (2026-09-14): all nine modern bundles passed live
  Journal launch/stop cleanup after the identity correction; final Browse/Log
  probes completed with `cleanup=PASS` (PIDs `277262`, `277292`).
- Direct QMP Space check (2026-09-14): with the QEMU window active, injected
  F7 and F8 events left the authoritative EWMH state at `current=1`; semantic
  `sugar-gtk4-space.sh` switching remains functional, so physical function-key
  delivery is still isolated as the transport gap.
- Guest evdev probe (2026-09-14): both QMP `input-send-event` and monitor
  `send-key f1` returned successfully but produced no events on the guest's
  QEMU USB/virtio keyboard devices. This localizes the failure below GTK4 and
  Metacity; no shell-side keybinding change is justified by this evidence.
- Native Mastermind Activity (2026-09-14): added a self-contained GTK4 logic
  game under the original `org.laptop.Mastermind` bundle identity. Guest build
  and the expanded ten-Activity Casilda matrix passed launch/stop cleanup
  (PID `280547`), closing one more legacy Activity port without changing shell
  lifecycle or Spaces architecture.
- Native Poll Activity (2026-09-14): added an editable-question, local-vote
  GTK4 Activity under `org.worldwideworkshop.PollBuilder`. The rebuilt guest
  and eleven-Activity Casilda matrix passed launch/stop cleanup (PID `283466`).
- Native Mancala Activity (2026-09-14): added a playable two-row pit/store
  GTK4 Activity under `mulawa.Mancala`. The rebuilt guest and twelve-Activity
  Casilda matrix passed launch/stop cleanup (PID `286396`).

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
