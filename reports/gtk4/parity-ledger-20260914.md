# GTK4 parity ledger — 2026-09-14

Native Abacus (2026-09-14): a GTK4 five-rod place-value Activity with
increment/decrement controls and computed value was staged under
`com.homegrownapps.abacus`. Three guest Casilda launch/stop cycles passed with
`cleanup=PASS` (PIDs `398910`, `398940`, `398961`).

Full 39-Activity matrix recheck (2026-09-14): all registered bundles completed
three guest Journal launch/stop cycles; all 117 cycles reported `cleanup=PASS`
and the matrix ended with `activity-matrix=PASS` (latest PID `402252`).

Native Color My World (2026-09-14): a GTK4 color palette and rendered swatch
Activity was staged under `org.sugarlabs.ColorMyWorldActivity`. Three guest
Casilda launch/stop cycles passed with `cleanup=PASS` (PIDs `393024`, `393052`,
`393077`).

Full 38-Activity matrix recheck (2026-09-14): all registered bundles completed
three guest Journal launch/stop cycles; all 114 cycles reported `cleanup=PASS`
and the matrix ended with `activity-matrix=PASS` (latest PID `396284`).

Native Game Of Life (2026-09-14): a GTK4 cellular-automaton grid with Step and
Clear controls was staged under `org.sugarlabs.gameOfLife`. Three guest Casilda
launch/stop cycles passed with `cleanup=PASS` (PIDs `390350`, `390378`, `390403`).

Native TurtleBlocks (2026-09-14): a GTK4 Logo-style turtle drawing canvas with
Forward, Turn right, and Clear controls was staged under
`org.laptop.TurtleArtActivity`. Three guest Casilda launch/stop cycles passed
with `cleanup=PASS` (PIDs `387676`, `387704`, `387729`).

Native Gears (2026-09-14): a GTK4 custom-rendered meshing-gear canvas with turn
and reset controls was staged under `org.sugarlabs.GearsActivity`. Three guest
Casilda launch/stop cycles passed with `cleanup=PASS` (PIDs `381805`, `381833`,
`381858`).

Native Stopwatch (2026-09-14): a GTK4 elapsed-time Activity with start/pause and
reset controls was staged under `org.sugarlabs.StopwatchActivity`. Three guest
Casilda launch/stop cycles passed with `cleanup=PASS` (PIDs `379133`, `379161`,
`379186`).

Native Grid Paint (2026-09-14): a GTK4 10×10 selectable drawing grid with a
clear action was staged under `org.olpcfrance.Gridpaint`. Three guest Casilda
launch/stop cycles passed with `cleanup=PASS` (PIDs `373650`, `373678`, `373703`).

Native Get Things Done (2026-09-14): a GTK4 task list with add and completion
tracking was staged under `org.sugarlabs.GTDActivity`. Three guest Casilda
launch/stop cycles passed with `cleanup=PASS` (PIDs `370984`, `371012`, `371037`).

Native Last One Loses (2026-09-14): a GTK4 take-away game with selectable
token counts and reset was staged under `org.olpc-france.LOLActivity`. Three
guest Casilda launch/stop cycles passed with `cleanup=PASS` (PIDs `365679`,
`365707`, `365732`).

Full 31-Activity matrix (2026-09-14): every registered GTK4 bundle completed
three guest Journal launch/stop cycles; all 93 cycles reported `cleanup=PASS`
and the matrix ended with `activity-matrix=PASS` (latest PID `368370`).

Full 33-Activity matrix recheck (2026-09-14): all registered bundles completed
three guest Journal launch/stop cycles; all 99 cycles reported `cleanup=PASS`
and the matrix ended with `activity-matrix=PASS` (latest PID `376518`).

Full 35-Activity matrix recheck (2026-09-14): all registered bundles completed
three guest Journal launch/stop cycles; all 105 cycles reported `cleanup=PASS`
and the matrix ended with `activity-matrix=PASS` (latest PID `384832`).

Cross-space regression (2026-09-14): GTK4 runtime checker passed on desktop 1
(`pid=265471`), semantic GTK3→GTK4 switching returned `current=1`, and the
separate GTK3 reference remained `pid=33761`; host suite passed 201 tests.

Native Words (2026-09-14): a GTK4 word exploration/translation Activity was
staged under `org.laptop.Words`. Three guest Casilda launch/stop cycles passed
with `cleanup=PASS` (PIDs `363015`, `363043`, `363068`).

Native Finance (2026-09-14): an income/expense tracker with balance calculation
was staged under `org.laptop.community.Finance`. Three guest Casilda
launch/stop cycles passed with `cleanup=PASS` (PIDs `360347`, `360375`, `360400`).

Native Markdown (2026-09-14): a GTK4 editor/preview Activity was staged under
`org.sugarlabs.Markdown`. Three guest Casilda launch/stop cycles passed with
`cleanup=PASS` (PIDs `357682`, `357710`, `357735`).

Native Portfolio (2026-09-14): a GTK4 document-canvas Activity with editable
title/body, draft status, and clear action was staged under
`org.sugarlabs.PortfolioActivity`. Three guest Casilda launch/stop cycles passed
with `cleanup=PASS` (PIDs `355014`, `355042`, `355067`).

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

Native Jumble repeated lifecycle (2026-09-14): three launch/stop cycles passed
with `cleanup=PASS` (PIDs `292333`, `292356`, `292377`).

Reversi game-state correction (2026-09-14): the board now detects a terminal
position when neither side has a legal move and reports the winner; three
post-fix lifecycle cycles passed with `cleanup=PASS` (PIDs `292840`–`292884`).

Native Number Rush (2026-09-14): arithmetic rounds and score tracking run as a
GTK4 Activity; three lifecycle cycles passed with `cleanup=PASS` (PIDs
`296505`–`296549`).

Native Across and Down (2026-09-14): a GTK4 crossword grid with clue
navigation, letter entry, and word checking was staged under the original
`mulawa.AcrossDown` identity. Three guest Casilda launch/stop cycles passed
with `cleanup=PASS` (PIDs `310738`, `310761`, `310782`).

Full sixteen-Activity matrix recheck (2026-09-14): all 48 guest launch/stop
cycles, including the new Across and Down bundle, reported `cleanup=PASS`; the
matrix ended with `activity-matrix=PASS` (Across and Down PIDs `311923`,
`311944`, `311966`).

Native IQ (2026-09-14): a GTK4 sequence-puzzle Activity was staged under the
original `mulawa.IQ` identity. Three guest Casilda launch/stop cycles passed
with `cleanup=PASS` (PIDs `314561`, `314584`, `314605`).

Native Appel Haken (2026-09-14): a GTK4 four-colour puzzle was staged under the
original `mulawa.AppelHaken` identity. Three guest Casilda launch/stop cycles
passed with `cleanup=PASS` (PIDs `318442`, `318465`, `318486`).

Eighteen-Activity matrix recheck (2026-09-14): all 54 guest launch/stop
cycles, including Appel Haken, reported `cleanup=PASS`; final result was
`activity-matrix=PASS` (Appel Haken PIDs `319764`, `319785`, `319806`).

Native BallAndBrick (2026-09-14): a GTK4 brick-breaker surface with pointer
interaction was staged under `org.sugarlabs.BallAndBrick`. Three guest Casilda
launch/stop cycles passed with `cleanup=PASS` (PIDs `322404`, `322427`, `322448`).

Native Implode (2026-09-14): a GTK4 matching-block puzzle was staged under
`com.jotaro.ImplodeActivity`. Three guest Casilda launch/stop cycles passed
with `cleanup=PASS` (PIDs `325047`, `325070`, `325092`).

Twenty-Activity matrix recheck (2026-09-14): all 60 guest launch/stop cycles
reported `cleanup=PASS`; final result was `activity-matrix=PASS` (Implode PIDs
`326514`, `326536`, `326558`).

Native PlayGo (2026-09-14): a GTK4 Go board with alternating stone placement
was staged under `org.laptop.PlayGo`. Three guest Casilda launch/stop cycles
passed with `cleanup=PASS` (PIDs `329171`, `329194`, `329215`).

Twenty-one-Activity matrix recheck (2026-09-14): all 63 guest launch/stop
cycles reported `cleanup=PASS`; final result was `activity-matrix=PASS`
(PlayGo PIDs `330778`, `330803`, `330828`).

Native BlockParty (2026-09-14): a GTK4 block-arrangement puzzle was staged
under `org.laptop.BlockPartyActivity`. Three guest Casilda launch/stop cycles
passed with `cleanup=PASS` (PIDs `333429`, `333457`, `333482`).

Twenty-two-Activity matrix recheck (2026-09-14): all 66 guest launch/stop
cycles reported `cleanup=PASS`; final result was `activity-matrix=PASS`
(BlockParty PIDs `335315`, `335340`, `335365`).

Native Typing Turtle (2026-09-14): a GTK4 typing exercise with real text input
was staged under `org.laptop.community.TypingTurtle`. Three guest Casilda
launch/stop cycles passed with `cleanup=PASS` (PIDs `338223`, `338251`, `338276`).

Twenty-three-Activity matrix recheck (2026-09-14): all 69 guest launch/stop
cycles reported `cleanup=PASS`; final result was `activity-matrix=PASS`
(Typing Turtle PIDs `340188`, `340213`, `340238`).

Native Memorize (2026-09-14): a GTK4 card-matching game was staged under
`org.laptop.Memorize`. Three guest Casilda launch/stop cycles passed with
`cleanup=PASS` (PIDs `342842`, `342870`, `342895`).

Twenty-four-Activity matrix recheck (2026-09-14): all 72 guest launch/stop
cycles reported `cleanup=PASS`; final result was `activity-matrix=PASS`
(Memorize PIDs `344894`, `344919`, `344944`).

Native Maze (2026-09-14): a GTK4 maze grid with keyboard/pointer movement was
staged under `vu.lux.olpc.Maze`. Three guest Casilda launch/stop cycles passed
with `cleanup=PASS` (PIDs `347548`, `347576`, `347601`).

Twenty-five-Activity matrix recheck (2026-09-14): all 75 guest launch/stop
cycles reported `cleanup=PASS`; final result was `activity-matrix=PASS`
(Maze PIDs `349688`, `349713`, `349739`).

Native FotoToon (2026-09-14): a GTK4 caption canvas with pointer placement and
text input was staged under `org.eq.FotoToon`. Three guest Casilda launch/stop
cycles passed with `cleanup=PASS` (PIDs `352343`, `352371`, `352396`).

Live shell recheck (2026-09-14): the GTK4 runtime checker reports
`target=gtk4 pid=265471 desktop=1 window=0x2400005` with the separate GTK3
reference `stable_pid=33761`; semantic Spaces switching GTK3 → GTK4 returns
`current=1`, preserving both process identities.

Host regression recheck (2026-09-14): the complete suite passes with 186 tests
(`pytest -q`).

Seventeen-Activity matrix recheck (2026-09-14): all 51 guest launch/stop
cycles, including IQ, reported `cleanup=PASS`; final result was
`activity-matrix=PASS` (IQ PIDs `315806`, `315827`, `315848`).

Number Rush scoring correction (2026-09-14): a solved round is now latched so
repeated Check activation cannot inflate the score; post-fix three-cycle
lifecycle passed with `cleanup=PASS` (PIDs `297682`–`297726`).

Count restore validation (2026-09-14): malformed layer shapes and non-numeric
selected-layer values now fall back safely; rebuilt guest lifecycle passed
three cycles with `cleanup=PASS` (PIDs `308057`–`308101`).

Full matrix recheck after Number Rush registration (2026-09-14): all fifteen
modern Activities completed three launch/stop cycles with `cleanup=PASS`; the
latest Jumble and Number Rush cycles used PIDs `297535`–`297650`.

Journal Projects filter (2026-09-14): GTK4 Journal now exposes a native
Projects toggle, filters rows by `project_id`, reports the filtered count, and
restores the correct empty-state text when toggled off. The guest overlay build
passed after these changes; targeted Journal tests pass.

Full matrix rerun (2026-09-14): all fourteen registered modern Activities
completed Journal launch/stop with `cleanup=PASS`; the matrix now defaults to
three cycles. The latest Reversi and Jumble cycles used PIDs `293799`–`293913`.

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
