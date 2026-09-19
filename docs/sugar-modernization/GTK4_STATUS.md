# GTK4 status

Status checked: 2026-09-15 (documentation synchronized after the README and
design-runbook refresh).

2026-09-15 correction: process cleanup alone did not prove safe closure or
document resume. Runtime testing found and fixed immediate shell SIGTERM
interrupting saves (0125) and missing Journal object arguments (0126).
Three real Write content save/stop/resume cycles now pass; see
`reports/gtk4/journal-save-resume-20260915.md` and the reproducible
`scripts/sugar-gtk4-journal-roundtrip.py` probe. Broader Activity behavior is
still classified separately from launch coverage.

| Component | Aspartame now | Upstream GTK3 | Upstream GTK4 | Usable today? | Blocker / action |
|---|---|---|---|---|---|
| Sugar shell | Arch `sugar 0.121-7`, plus isolated GTK4 preview source | Working X11 shell | GTK4 preview shell starts in a separate process | GTK3 and GTK4 preview | Keep GTK3 stable; compare behavior in the modern Space |
| Toolkit | GTK3 and GTK4 toolkits remain separate | Mature GTK3 API | `sugar-toolkit-gtk4` `sugar4` APIs | GTK4 shell usable | Keep GTK3/GTK4 out of one GI process |
| Artwork | Arch `sugar-artwork`, normalized icon pipeline | Working GTK3 theme | GTK4 renderer consumes activity metadata/XOColor semantics; Home and palettes share a bundle-icon resolver with a logged Sugar fallback | GTK3 and GTK4 preview | Keep artwork ownership upstream-compatible; per-Activity visual normalization remains deferred |
| Datastore | Arch `sugar-datastore` | Working Carquinyol service | No independent GTK4 datastore requirement identified | Yes as a service | Keep D-Bus/service boundary stable |
| Fructose activities | Arch packages plus pinned bundled set | Mixed but runnable | Fifty modern Activities are registered; the 2026-09-19 live matrix passed every bundle through Journal launch, activation, stop, and cleanup | Runtime coverage and behavioral parity are separate; see `ACTIVITY_PORT_CLASSIFICATION.md` | Do not treat registration or launch coverage as a full port |
| Display/session | Xorg + Metacity + `sugar-runner` assumptions | Supported | Casilda owns the private Activity surface inside the GTK4 preview | GTK4 preview on X11 host | Keep the Casilda boundary; do not claim a full Wayland session |
| Calculate | GTK3 Activity | Native GTK4 bundle | Safe arithmetic editor registered in the modern prefix | GTK4 verified 2026-09-14 | `org.aspartame.Calculate` launches through Journal and stops cleanly |
| Image Viewer | GTK3 Activity | Pinned GTK4 source | Registered from the GTK4 port without shell changes | GTK4 verified 2026-09-14 | `org.laptop.ImageViewerActivity` launches and stops cleanly |
| Terminal | GTK3 Activity | Native GTK4 command/output bundle under the original identity | GTK4 text output and command entry, without GTK3 Vte import | GTK4 verified 2026-09-15 | `org.laptop.Terminal` accepts a command, renders output, and stops cleanly; full emulator features remain bounded |
| Browse | Native GTK4 URL/status surface; pinned WebKit source retained for future renderer work | Guest `webkitgtk-6.0` installed | WebKit remains an Activity-specific optional dependency | GTK4 verified 2026-09-15 | Journal launch, visible URL entry, load status, stop, and cleanup all pass in live guest |
| Clock | GTK3 Activity | Native GTK4 bundle | Live GTK4 time/date label | GTK4 verified 2026-09-14 | `tv.alterna.Clock` launches and stops cleanly through Casilda |
| JAMClock | GTK3/Pygame Activity | Native GTK4 bundle | GTK4 time/date replacement under the original bundle ID | GTK4 verified 2026-09-14 | `org.laptop.JAMClock` launches and stops cleanly through Casilda |
| Mastermind, Poll, Mancala, Reversi, Jumble, NumberRush, Across and Down, IQ, Appel Haken, BallAndBrick, Implode, PlayGo, BlockParty, Typing Turtle, Memorize, Maze, FotoToon, Portfolio, Markdown, Finance, Words, Last One Loses, Grid Paint, Gears, TurtleBlocks, Game Of Life, Color My World, Abacus, Planets, Connect the Dots, Pippy, Paint, Diamond Fusion, Level, Moon | GTK3 legacy Activities | Native GTK4 bundles | Self-contained logic, survey, board, word, arithmetic, crossword, sequence, colour, brick-breaker, matching-block, Go-board, block-arrangement, typing, card-matching, maze, caption-canvas, document-canvas, Markdown editor, budget-tracking, language, take-away game, grid-drawing, custom gear-rendering, Logo-style turtle drawing, cellular-automaton, color-palette, place-value, orbit-canvas, numbered-dot puzzle, Python playground, drawing-canvas, matching/fusion puzzle, inclination-control, and moon-phase interactions | GTK4 verified 2026-09-14 | Planets, Connect the Dots, Pippy, Paint, Diamond Fusion, Level, and Moon are included in direct lifecycle probes |
| Get Things Done | GTK3 legacy Activity | Native GTK4 bundle | Task list with add/complete controls and JSON Journal persistence | GTK4 verified 2026-09-15 | Two real launch/stop/resume cycles pass; collaboration and full upstream feature breadth remain unclaimed |
| Level | GTK3 legacy Activity | Native GTK4 bundle | Offline spirit-level controls with drag/keyboard adjustment and JSON Journal persistence | GTK4 verified 2026-09-15 | Two real launch/stop/resume cycles pass; hardware orientation sensors remain unclaimed |
| Markdown | GTK3 legacy Activity | Native GTK4 bundle | UTF-8 editor, live preview, and Journal persistence | GTK4 verified 2026-09-15 | Two real launch/stop/resume cycles pass; full parser/rendering parity remains unclaimed |
| Write | GTK3 legacy Activity | Native GTK4 bundle | Document editor with draft status and clear action | GTK4 verified 2026-09-14 | `org.sugarlabs.Write` passes three direct Casilda lifecycle cycles |
| Read | GTK3 legacy Activity | Native GTK4 bundle | UTF-8 text reader with form-feed pages and Journal resume | GTK4 verified 2026-09-15 | `org.laptop.sugar.ReadActivity` resumes seeded Journal text objects; PDF/EPUB parity is not claimed |
| Stopwatch | GTK3 legacy Activity | Native GTK4 bundle | Elapsed-time display with JSON Journal resume | GTK4 verified 2026-09-15 | `org.sugarlabs.StopwatchActivity` resumes seeded elapsed-time objects; lap/export parity is not claimed |

Current verified checkpoint: GTK4 Home Favorites/List/search, Frame,
native Journal Activity search/resume/edit/selection, Settings navigation,
Neighborhood/Group empty states, Sugar palettes, clipboard transfer, Help,
Activity Manager policy, and repeated normal/abnormal Activity launch-stop
cleanup run in the modern Space. Native Journal and Home List launch paths
have real Casilda Activity-surface and process evidence. The complete matrix
is maintained in `reports/gtk4/runtime-matrix-20260914.md` (with the earlier
2026-09-13 report retained as historical evidence).

Remaining limits are explicit: physical F1-F6 delivery is below the current
QEMU/evdev transport; Neighborhood collaboration cannot be exercised without
peers; and additional legacy Activities remain individual porting targets.
These are not silently counted as GTK4 parity.

The shell-level `ShowJournal()` action now presents the native Journal surface
in the modern Space. A 1920x1080 capture shows search, project controls, 415
entries, row actions, and the Sugar frame; native Journal Activity
launch/resume remains independently verified as a separate lifecycle path.

TurtleBlocks is now classified as a FUNCTIONAL PORT for its bounded drawing
workflow. The guest round-trip probe discovers the mapped activity surface by
real process ID through AT-SPI, restores seeded position/heading/line data from
Journal, and verifies clean process and D-Bus cleanup. Full upstream Logo block
language, collaboration, and feature breadth remain intentionally unclaimed;
see `reports/gtk4/turtleart-runtime-20260915.md`.

The ISO profile includes GTK4 runtime libraries, but the GTK4 source overlay
and pinned Activity checkouts are still supplied by the `aspartame-dev` 9p
share during development. Embedding those sources into a standalone ISO is a
separate packaging task and is not yet claimed.

The GTK4 toolkit repository describes itself as a GTK4 toolkit and documents
`sugar4` APIs, while the main Sugar repository still documents GTK3 toolkit
dependencies. Aspartame therefore keeps the stable GTK3 Space as a behavioral
reference while operating a separately tested GTK4 preview Space. The preview
is materially usable, but the full completion gate is not claimed because the
physical function-key transport, peer collaboration, and complete Activity
catalog remain open.

References:

- https://github.com/sugarlabs/sugar-toolkit-gtk4
- https://github.com/sugarlabs/sugar
- https://github.com/sugarlabs/GSoC/blob/master/Ideas-2026.md
- https://github.com/sugarlabs/sugar-runner
