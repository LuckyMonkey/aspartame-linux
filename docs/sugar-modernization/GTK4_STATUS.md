# GTK4 status

Status checked: 2026-10-04 (documentation synchronized after the GTK4 UX and
Chirality milestone pass).

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
| Fructose activities | Arch packages plus pinned bundled set | Mixed but runnable | Fifty-one modern Activities are registered; the original 50-bundle live matrix passed Journal launch, activation, stop, and cleanup, and Record now has a direct headless guest lifecycle receipt | Runtime coverage and behavioral parity are separate; see `ACTIVITY_PORT_CLASSIFICATION.md` | Do not treat registration or launch coverage as a full port |
| Display/session | Xorg + Metacity + `sugar-runner` assumptions | Supported | Casilda owns the private Activity surface inside the GTK4 preview | GTK4 preview on X11 host | Keep the Casilda boundary; do not claim a full Wayland session |
| Calculate | GTK3 Activity | Native GTK4 bundle | Safe arithmetic editor with functions, variables, history, angle mode, and bounded exponent/factorial evaluation | GTK4 lifecycle verified; expanded host harness verified 2026-10-04 | `org.aspartame.Calculate` launches through Journal and stops cleanly; full GTK3 feature parity remains open |
| Image Viewer | GTK3 Activity | Pinned GTK4 source | Registered from the GTK4 port without shell changes | GTK4 verified 2026-09-14 | `org.laptop.ImageViewerActivity` launches and stops cleanly |
| Terminal | GTK3 Activity | Native GTK4 command/output bundle under the original identity | GTK4 text output and command entry, without GTK3 Vte import | GTK4 verified 2026-09-15 | `org.laptop.Terminal` accepts a command, renders output, and stops cleanly; full emulator features remain bounded |
| Browse | Native GTK4 URL/status surface; pinned WebKit source retained for future renderer work | Guest `webkitgtk-6.0` installed | WebKit remains an Activity-specific optional dependency | GTK4 verified 2026-09-15 | Journal launch, visible URL entry, load status, stop, and cleanup all pass in live guest |
| Clock | GTK3 Activity | Native GTK4 bundle | Responsive GTK4 learning clock with simple/nice/digital faces, date/words/ticking/speech controls, hand adjustment, and Journal state | GTK4 lifecycle plus focused control/resume harness verified 2026-10-04 | `tv.alterna.Clock` launches and stops cleanly through Casilda; NTP time setting and the full upstream visual breadth remain open |
| JAMClock | GTK3/Pygame Activity | Native GTK4 bundle | Responsive GTK4 analog clock, calendar, configurable alarm, and Journal state under the original bundle ID | GTK4 lifecycle plus focused control/resume and headless visual qualification verified 2026-10-04 | `org.laptop.JAMClock` launches and stops cleanly through Casilda; legacy Pygame artwork/audio breadth remains open |
| Diamond Fusion | GTK3 legacy Activity | Native GTK4 bundle | Responsive labeled puzzle board, neighbour matching/fusion interaction, score feedback, and Journal board/score state | GTK4 lifecycle, focused harness, and headless board-click visual qualification verified 2026-10-04 | `com.francocorrea.diamondfusion` launches and stops cleanly through Casilda; full cascade/scoring breadth and collaboration remain open |
| Moon | GTK3 legacy Activity | Native GTK4 bundle | Responsive labeled phase canvas, visible moon illustration, phase navigation, and Journal phase state | GTK4 lifecycle, focused harness, and headless phase-transition visual qualification verified 2026-10-04 | `com.garycmartin.Moon` launches and stops cleanly through Casilda; full astronomical simulation remains open |
| Pippy | GTK3 legacy Activity | Native GTK4 bundle | Responsive side-by-side Python editor/output workspace, examples, program input, bounded execution, and cancellation | GTK4 lifecycle, focused runner qualification, and headless Run visual qualification verified 2026-10-04 | `org.laptop.Pippy` launches and runs the default program through Casilda; full upstream editor/runtime breadth remains open |
| Connect the Dots | GTK3 legacy Activity | Native GTK4 bundle | Responsive labeled dot canvas, numbered point selection, visible connection progress, and Journal progress state | GTK4 lifecycle, focused harness, and headless point-click visual qualification verified 2026-10-04 | `org.sugarlabs.ConnectTheDots` launches and accepts point input through Casilda; full artwork and collaboration breadth remain open |
| Jukebox | GTK3 legacy Activity | Native GTK4 bundle | Responsive Playlist/Player workspace, offline demo-track selection, play/stop state, optional native GStreamer playback for local URIs, and Journal playlist state | GTK4 lifecycle, focused harness, and headless Play visual qualification verified 2026-10-04; local-playback path deployed and lifecycle-checked 2026-10-05 | `org.laptop.sugar.Jukebox` launches and updates playback state through Casilda; codec coverage and real media-device qualification remain open |
| Portfolio | GTK3 legacy Activity | Native GTK4 bundle | Responsive labeled project-description editor, title/body editing, draft-save state, and Journal project state | GTK4 lifecycle, focused harness, and headless title/save visual qualification verified 2026-10-04 | `org.sugarlabs.PortfolioActivity` launches and saves draft state through Casilda; rich media/export breadth remains open |
| Write | GTK3 legacy Activity | Native GTK4 bundle | Responsive labeled document editor, UTF-8 editing, draft-save state, and Journal document state | GTK4 lifecycle, focused harness, and headless text/save visual qualification verified 2026-10-04 | `org.sugarlabs.Write` launches and saves a five-character draft through Casilda; rich text and upstream document-format parity remain open |
| Mastermind, Poll, Mancala, Reversi, Jumble, NumberRush, Across and Down, IQ, Appel Haken, BallAndBrick, Implode, PlayGo, BlockParty, Typing Turtle, Memorize, Maze, FotoToon, Finance, Words, Last One Loses, Grid Paint, Gears, TurtleBlocks, Game Of Life, Color My World, Abacus, Planets, Paint, Level | GTK3 legacy Activities | Native GTK4 bundles | Self-contained logic, survey, board, word, arithmetic, crossword, sequence, colour, brick-breaker, matching-block, Go-board, block-arrangement, typing, card-matching, maze, caption-canvas, document-canvas, budget-tracking, language, take-away game, grid-drawing, custom gear-rendering, Logo-style turtle drawing, cellular-automaton, color-palette, place-value, orbit-canvas, drawing-canvas, inclination-control | GTK4 verified 2026-09-14 | Planets, Paint, and Level are included in direct lifecycle probes |
| Get Things Done | GTK3 legacy Activity | Native GTK4 bundle | Task list with add/complete/remove/reorder controls and JSON Journal persistence | GTK4 verified 2026-09-15; bounded task parity improved 2026-10-05 | Two real launch/stop/resume cycles pass; collaboration and full upstream feature breadth remain unclaimed |
| Level | GTK3 legacy Activity | Native GTK4 bundle | Offline spirit-level controls with drag/keyboard adjustment and JSON Journal persistence | GTK4 verified 2026-09-15 | Two real launch/stop/resume cycles pass; hardware orientation sensors remain unclaimed |
| Markdown | GTK3 legacy Activity | Native GTK4 bundle | Responsive side-by-side Markdown source/preview workspace with starter content and Journal source state | GTK4 lifecycle, focused harness, and headless preview visual qualification verified 2026-10-04 | `org.sugarlabs.Markdown` launches cleanly and mirrors starter source into Preview through Casilda; full parser/rendering parity remains open |
| Write | GTK3 legacy Activity | Native GTK4 bundle | Document editor with draft status and clear action | GTK4 verified 2026-09-14 | `org.sugarlabs.Write` passes three direct Casilda lifecycle cycles |
| Read | GTK3 legacy Activity | Native GTK4 bundle | Responsive labeled Reading page, UTF-8 text reader with form-feed pages, navigation, and Journal resume | GTK4 lifecycle, focused harness, and headless Next-page visual qualification verified 2026-10-04 | `org.laptop.sugar.ReadActivity` resumes seeded Journal text objects; PDF/EPUB parity is not claimed |
| Stopwatch | GTK3 legacy Activity | Native GTK4 bundle | Elapsed-time display with JSON Journal resume | GTK4 verified 2026-09-15 | `org.sugarlabs.StopwatchActivity` resumes seeded elapsed-time objects; lap/export parity is not claimed |
| Record | GTK3 Activity | Native GTK4 bundle | GStreamer-backed photo, video, and audio capture model with zip Journal resume and path-traversal refusal | Host capture harness and one-cycle headless guest lifecycle verified 2026-10-04 | `scripts/sugar-gtk4-record-roundtrip.py` passes seeded photo resume, media preservation, AT-SPI visibility, service release, and shell cleanup; camera/viewfinder, timers, per-capture Journal objects, and collaboration remain open |

Current verified checkpoint: GTK4 Home Favorites/List/search, Frame,
native Journal Activity search/resume/edit/selection, Settings navigation,
Neighborhood/Group empty states, Sugar palettes, clipboard transfer, Help,
Activity Manager policy, and repeated normal/abnormal Activity launch-stop
cleanup run in the modern Space. Native Journal and Home List launch paths
have real Casilda Activity-surface and process evidence. The complete matrix
is maintained in `reports/gtk4/runtime-matrix-20260914.md` (with the earlier
2026-09-13 report retained as historical evidence).

Remaining limits are explicit: Neighborhood collaboration cannot be exercised
without a second peer; and additional legacy Activities remain individual
porting targets. Headless QMP F7/F8 Space selection is now qualified on the
2026-10-04 image; host-window pointer/grab behavior remains a separate
convenience check. These limits are not silently counted as GTK4 parity.

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

The ISO profile now embeds the GTK4 preview root, generated prefix, helper
scripts, and pinned Activity trees under `/usr/lib/aspartame/gtk4-preview`.
The 2026-09-19 shareless boot evidence is recorded in
`reports/gtk4/standalone-image-runtime-20260919.md`; `aspartame-dev` is now an
optional development override rather than a runtime dependency. A clean
writable data-disk reboot and Journal resume now pass on disposable disks;
see `reports/gtk4/journal-reboot-persistence-20261004.md`.

The GTK4 toolkit repository describes itself as a GTK4 toolkit and documents
`sugar4` APIs, while the main Sugar repository still documents GTK3 toolkit
dependencies. Aspartame therefore keeps the stable GTK3 Space as a behavioral
reference while operating a separately tested GTK4 preview Space. The preview
is materially usable, but the full completion gate is not claimed because peer
collaboration and complete Activity parity remain open.

The 2026-10-04 development qualification passed the complete 50-bundle GTK4
visual sweep at 1920x1080 after the shared heading-theme fix. Focused UX
follow-ups corrected Abacus's stretched rod controls, Finance's full-width
empty workspace, and empty-state affordances in Pippy, Color My World, and
Words. Color My World now also exposes an instruction-led palette with
visible selected state, a bounded clickable world-region map, a clear action,
and accessible color controls. Calculate and Paint then
received richer responsive workspaces, and
Pippy gained examples, program input, indentation, Ctrl+Enter, and traceback
line navigation on the bounded runner. The full host suite is green at
`536 passed`.

The 2026-10-05 Abacus UX pass replaced the stretched edge-to-edge rod grid with
a centered, width-constrained work card, readable place labels, a prominent
current-value card, and stable increase/decrease controls. Each rod now also
offers direct clickable bead positions while retaining the +/- controls for
keyboard and assistive-technology users. A headless 1920x1080 capture confirms
the seeded `12,345` value and centered layout; the guest Journal resume/lifecycle
receipt passes independently. This remains a
FUNCTIONAL PORT because advanced bead manipulation is not yet reproduced.

The 2026-10-05 Markdown UX pass now makes the source/preview relationship
explicit with framed equal panes, a readable monospace source editor, a guided
empty-source state, top-aligned preview content, and a concise character-count
footer. The preview now renders a sanitized common Markdown subset (headings,
emphasis, code, links, lists, quotes, and rules) as GTK-native Pango markup;
raw source HTML cannot become widget markup. The guest Journal resume/lifecycle
receipt still passes; full CommonMark/PageDown parser parity remains open.

The 2026-10-05 Finance pass adds object-specific transaction Remove actions,
fresh-row rebuilding, and removal persistence. The headless receipt removes a
seeded expense, verifies the resulting `125.50` balance and one-row Journal
payload, and captures the aligned table. Finance now also has accessible CSV
Import/Export actions backed by a tested description/amount/type interchange
module; chart views and collaboration remain outside the bounded port.

Chirality Milestone 1 now has a real GTK4-only Activity adapter and a guest
probe that switches Calculate and Clock Left/Right/Left on one visible
surface, then verifies Activity service cleanup. This advances the forward
path without removing GTK3 or repurposing migration comparison keys.

Chirality Milestone 2 is now qualified for the bounded UTF-8 object path. The
guest probe creates one Journal UID in Write, resumes that same object in
Write and Read, assigns both live GTK4 Activities to semantic hands, switches
Left/Right/Left, and verifies the final payload plus service cleanup. Broader
object-format refusal and session-resume gates remain open; GTK3 retirement is
therefore still evidence-gated.

The Chirality model now keeps object handoff and Activity identity separate:
handoff copies only the source object's reference/title while preserving the
target hand's Activity and bundle identity. The invariant is covered by the
focused semantic suite; no split-screen or history state was introduced.

The held-Activity crash gate is independently qualified: terminating the
Right GTK4 Activity leaves Left alive and activatable, then clears only the
exited hand through the Chirality adapter. Activity replacement/resume and a
real two-shell GTK4 restart are also qualified for a Journal UID; unsupported
object-capability refusal remains open before user-facing handoff actions.

The 2026-10-04 Clock parity pass replaced the former two-label GTK4 surface
with a scalable clock face and responsive controls. Simple and nice analog
faces, digital mode, date/words/ticking options, optional speech, GTK4 hand
dragging, malformed Journal input handling, and stable Journal resume are now
covered by the focused harness. This is still a FUNCTIONAL PORT: the
platform-specific NTP/hardware-clock action is deliberately not claimed. See
`reports/gtk4/clock-parity-pass-20261004.md`.

The 2026-10-04 JAMClock parity pass replaced its former two-label surface
with a responsive analog face, GTK4 Calendar, alarm hour/minute controls,
alarm enable/status feedback, accessible labels, and stable JSON Journal
state. The headless guest receipt is in
`reports/gtk4/jamclock-parity-pass-20261004.md`; this remains a FUNCTIONAL
PORT because the original Pygame artwork and bundled alarm/ticking audio are
not reproduced.

The Activity-sharing harness now separates owner publication from peer join:
the owner share path passes and the peer probe exercises the real
`sugar4.presence.Activity.join()` contract. The current clean-shell run still
timed out before the second guest discovered the public Activity, so
Neighborhood/Group Activity join remains open.

Pippy now has a bounded Python execution boundary rather than a bare
`subprocess.run`: isolated working directory/interpreter mode, child resource
limits, process-group timeout cleanup, and stale-result suppression are
qualified by `scripts/sugar-gtk4-pippy-runtime-probe.py`. The editor now also
offers examples, stdin, Python indentation, Ctrl+Enter, traceback line
selection, and a Stop action that cancels the complete child process group
while retaining the same Journal payload. This is useful Python runtime
progress, not a claim of a security sandbox or full upstream Pippy parity.

The 2026-10-05 Pippy integration receipt now drives the visible GTK4 Run
button through that boundary, verifies captured `Aspartame` output and the
Finished status through AT-SPI, and captures the completed output workspace.
This closes the UI-to-runner handoff for the bounded path; sandboxing and full
upstream Pippy breadth remain open.

Snakepit's next runtime boundary is now connected to the GTK4 Activity
Manager. It discovers user-owned qualification records, labels them `Snakepit
Python`, exposes only passing records with a valid environment and explicit
launch contract as `Launch`, and keeps failed/incomplete records `Not ready`
and non-removable. The launcher inherits the qualified environment rather
than system Python. This is explicit v0 contract integration; dependency
resolution, security sandboxing, and broad Activity Manager discovery remain
open. See `reports/python/activity-manager-snakepit-20261004.md`.

References:

- https://github.com/sugarlabs/sugar-toolkit-gtk4
- https://github.com/sugarlabs/sugar
- https://github.com/sugarlabs/GSoC/blob/master/Ideas-2026.md
- https://github.com/sugarlabs/sugar-runner
