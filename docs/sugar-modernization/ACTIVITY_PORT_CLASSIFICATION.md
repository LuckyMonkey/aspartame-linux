# GTK4 Activity port classification

Runtime launch/stop coverage and behavioral parity are separate claims. The
matrix proves that a bundle can be resolved, shown through the GTK4 launcher,
started through Journal/Casilda, and stopped cleanly. It does not prove that
the GTK4 implementation contains every feature of the original Activity.

Classification used by the migration ledger:

- **FULL PORT** — core user workflow, persistence/object behavior, and normal
  interaction semantics are demonstrated against the GTK3 reference.
- **FUNCTIONAL PORT** — the principal offline workflow is usable, but feature
  breadth or collaboration/persistence parity is intentionally reduced.
- **COVERAGE IMPLEMENTATION** — a native GTK4 surface exists primarily to
  exercise registry, rendering, input, and lifecycle integration; it is not a
  parity claim.
- **PLACEHOLDER** — launchable shell-facing stub with no credible equivalent
  workflow. These must not be counted toward the retirement gate.

## Current classification

| Activity | Class | Evidence / boundary |
| --- | --- | --- |
| Help | FUNCTIONAL PORT | Native topic/help surface; shell-wide Help parity still separate |
| Count | FUNCTIONAL PORT | Native voxel/grid interaction; advanced layer behavior remains separate |
| Calculate | FUNCTIONAL PORT | Safe arithmetic editor; not a claim of full upstream feature parity. Update 2026-10-02 (host-verified, guest pending): functions, pi/e, `ans`, variables, `^`, degrees/radians, clickable history, specific error messages; fixed an unbounded power that could stall the Activity and an uncaught float overflow. Plotting and number bases remain absent |
| Clock | FUNCTIONAL PORT | Responsive simple/nice/digital clock faces, date/words/ticking controls, optional speech, GTK4 hand dragging, and stable Journal state verified 2026-10-04; NTP/hardware-clock actions remain absent |
| JAMClock | FUNCTIONAL PORT | Responsive analog clock, GTK4 calendar, configurable alarm, and stable Journal state verified 2026-10-04; legacy Pygame artwork/audio breadth remains absent |
| Diamond Fusion | FUNCTIONAL PORT | Responsive labeled puzzle-board surface, neighbour matching/fusion interaction, visible score, JSON Journal board/score resume, and clean stop verified 2026-10-04; full cascade/scoring breadth and collaboration remain absent |
| Moon | FUNCTIONAL PORT | Responsive labeled phase canvas, visible moon illustration, phase navigation, and JSON Journal phase resume verified 2026-10-04; full astronomical simulation remains absent |
| Image Viewer | FUNCTIONAL PORT | Native image surface through the pinned bundle path |
| Terminal | FUNCTIONAL PORT | Native GTK4 command/output surface, command input, and clean lifecycle verified 2026-09-15; full terminal-emulator features remain outside this claim |
| Browse | FUNCTIONAL PORT | Native GTK4 URL/status surface; full WebKit browsing and collaboration/download parity is not claimed |
| Log | FUNCTIONAL PORT | Native log list surface |
| Read | FUNCTIONAL PORT | Responsive labeled Reading page, UTF-8 Journal text object resume, visible page restoration and navigation, and clean stop verified 2026-10-04; PDF/EPUB/format breadth and upstream Read parity remain absent |
| Write | FUNCTIONAL PORT | Responsive labeled document editor, UTF-8 text editing, visible draft-save state, Journal save/stop/resume, and save-failure cancellation/retry verified 2026-10-04; rich text and upstream document-format parity remain absent |
| NumberRush | FUNCTIONAL PORT | Arithmetic round/check/next workflow, JSON Journal round/score resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full difficulty progression and collaboration breadth remain absent |
| Poll | FUNCTIONAL PORT | Question/choice editing, vote/reset workflow, JSON Journal save/resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; collaboration and upstream feature breadth remain absent |
| Mancala | FUNCTIONAL PORT | Two-row board movement, turn/store state, JSON Journal save/resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full rule/scoring and collaboration breadth remain absent |
| Reversi | FUNCTIONAL PORT | Eight-by-eight capture/flip workflow, board/player JSON Journal resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full scoring, hints, and collaboration breadth remain absent |
| Jumble | FUNCTIONAL PORT | Word scramble/check/next workflow, JSON Journal puzzle-index resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; scoring, hints, and collaboration breadth remain absent |
| Mastermind | FUNCTIONAL PORT | Four-color guess/check/reset workflow, visible guess progress, JSON Journal save/resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full upstream scoring, hints, and collaboration breadth remain absent |
| BlockParty | FUNCTIONAL PORT | Block rotation/arrangement workflow, JSON Journal arrangement resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full puzzle breadth and collaboration remain absent |
| PlayGo | FUNCTIONAL PORT | 5×5 stone placement/turn workflow, JSON Journal board/turn resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; captures, scoring, and collaboration breadth remain absent |
| Implode | FUNCTIONAL PORT | Matching-block removal workflow, visible remaining-block state, JSON Journal grid resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full cascade/scoring and collaboration breadth remain absent |
| BallAndBrick | FUNCTIONAL PORT | Pointer brick-hit workflow, visible remaining-brick state, JSON Journal brick-count resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full physics and collaboration breadth remain absent |
| Appel Haken | FUNCTIONAL PORT | Four-region colour cycling/validation, JSON Journal colour configuration resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full map breadth and collaboration remain absent |
| IQ | FUNCTIONAL PORT | Visual sequence choices, puzzle progression, JSON Journal round resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full puzzle catalog and collaboration breadth remain absent |
| Across and Down | FUNCTIONAL PORT | Crossword clue/letter editing and check workflow, JSON Journal clue/letters resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full crossword grid breadth and collaboration remain absent |
| Maze | FUNCTIONAL PORT | Four-direction movement, direct cell selection, JSON Journal position resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full maze generation and collaboration breadth remain absent |
| Memorize | FUNCTIONAL PORT | Card reveal/matching workflow, JSON Journal card/match resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full randomization, scoring, and collaboration breadth remain absent |
| Words | FUNCTIONAL PORT | UTF-8 word entry, lookup result, and JSON Journal save/resume verified with real GTK4 Activity processes on 2026-09-15; translation/audio breadth remains absent |
| Portfolio | FUNCTIONAL PORT | Responsive labeled project-description editor, UTF-8 title/body editing, visible draft-save state, and JSON Journal save/resume verified 2026-10-04; rich media/export breadth remains absent |
| FotoToon | FUNCTIONAL PORT | Caption canvas interaction and JSON Journal save/resume verified with real GTK4 Activity processes on 2026-09-15; image import/layout breadth remains absent |
| Finance | FUNCTIONAL PORT | Income/expense tracking, aligned transaction table, object-specific Remove actions, balance calculation, tested CSV description/amount/type interchange, and JSON Journal removal/save-resume verified in the headless guest on 2026-10-05; chart views and collaboration remain absent |
| Markdown | FUNCTIONAL PORT | Responsive centered side-by-side Markdown source/preview workspace with readable pane framing, guided empty state, sanitized common Markdown rendering (headings, emphasis, code, links, lists, quotes, and rules), and Journal save/resume verified in the headless guest on 2026-10-05; full CommonMark/PageDown parser parity remains absent |
| Stopwatch | FUNCTIONAL PORT | JSON Journal elapsed-time resume, visible time restoration, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; lap/export/collaboration breadth is not claimed |
| TurtleBlocks | FUNCTIONAL PORT | Forward/turn/clear drawing workflow, visible position/heading state, seeded JSON Journal turtle position/heading/lines resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full Logo block language, collaboration, and upstream feature breadth remain absent |
| Gears | FUNCTIONAL PORT | Native gear rendering/rotation controls, visible rotation state, JSON Journal phase resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; animation and collaboration breadth remain absent |
| Last One Loses | FUNCTIONAL PORT | Take-away turn workflow, visible token count, JSON Journal pile resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; strategy/AI and collaboration breadth remain absent |
| Grid Paint | FUNCTIONAL PORT | 10×10 cell painting, selection summary, and JSON Journal save/resume verified with real GTK4 Activity processes on 2026-09-15; advanced layer/fill tools remain absent |
| Get Things Done | FUNCTIONAL PORT | Native task list with add/complete/remove/reorder controls and JSON Journal order/completion save/resume; focused parity pass 2026-10-05 closes the bounded task-management contract, while collaboration and upstream feature breadth remain unclaimed |
| Abacus | FUNCTIONAL PORT | Centered five-rod place-value workspace with readable value hierarchy, constrained controls, computed value, and JSON Journal save/resume verified in the headless guest on 2026-10-05; advanced bead manipulation remains absent |
| Planets | FUNCTIONAL PORT | Responsive labeled solar-system canvas with deterministic star field, selected-planet highlight/details, planet navigation, and JSON Journal selection resume verified 2026-10-04; full simulation breadth remains absent |
| Color My World | FUNCTIONAL PORT | Instruction-led palette selection with visible selected state, rendered swatch, accessible color actions, and JSON Journal color resume; full artwork/collaboration breadth remains absent |
| Game Of Life | FUNCTIONAL PORT | Finite-grid stepping, live-cell selection, generation summary, and JSON Journal resume verified with real GTK4 Activity processes on 2026-09-15; advanced patterns/collaboration remain absent |
| Connect the Dots | FUNCTIONAL PORT | Responsive labeled dot canvas, numbered point selection, visible connection progress, JSON Journal progress resume, and clean stop verified 2026-10-04; full artwork and collaboration breadth remain absent |
| Pippy | FUNCTIONAL PORT | Responsive side-by-side Python editor/output workspace, UTF-8 source editing, visible Run-to-output integration with the bounded local runner, captured output/error/timeout handling, and Journal save/resume verified in the headless guest on 2026-10-05; full upstream editor/runtime breadth remains absent |
| Typing Turtle | FUNCTIONAL PORT | Keyboard exercise progression and JSON Journal exercise-index resume verified with real GTK4 Activity processes on 2026-09-15; scoring/audio breadth remains absent |
| Paint | FUNCTIONAL PORT | Pointer stroke drawing, color selection, and JSON Journal save/resume verified with real GTK4 Activity processes on 2026-09-15; image layers/tools remain absent. Update 2026-10-02 (host-verified, guest pending): pencil, line, rectangle, ellipse, and eraser tools; four brush sizes; eight colours plus a custom colour chooser; undo/redo with an undoable Clear; PNG export. v1 drawings load unchanged. Text, fill, image import, and layers remain absent |
| Level | FUNCTIONAL PORT | Offline inclination controls, drag interaction, and JSON Journal resume verified with real GTK4 Activity processes on 2026-09-15; hardware sensor integration remains outside this claim |
| Jukebox | FUNCTIONAL PORT | Responsive Playlist/Player workspace, offline track selection, visible play/stop state, optional native GStreamer playbin for local audio URIs, local-track metadata, and JSON Journal save/resume verified 2026-10-04/2026-10-05; codec coverage and media-device qualification remain absent |
| Get Books | FUNCTIONAL PORT | Offline catalog search, selected-book metadata, and JSON Journal query/selection resume verified with real GTK4 Activity processes on 2026-09-15; network catalogs/downloads remain absent |
| Record | FUNCTIONAL PORT | Host GStreamer capture harness plus one-cycle headless guest lifecycle verified 2026-10-04: seeded photo Journal resume, media preservation, AT-SPI visibility, service release, and shell cleanup; live camera/viewfinder, timers, per-capture Journal objects, video sound, and collaboration remain absent |

Record's host capture and guest lifecycle receipts are recorded in
`reports/gtk4/record-roundtrip-20261004.md`; its bounded functional-port
classification does not claim live camera hardware, timers, per-capture
Journal objects, video sound, or collaboration.

### Catalog-only Sugarizer entries

The review inventory contains 61 rows with `format=sugarizer-web`. Those are
source catalog records, not installed GTK4 implementations. They remain
unported; PLACEHOLDER specifically describes an implemented launchable stub.
Catalog membership alone does not establish any of the four port classes.
Several IDs also have native GTK4 coverage implementations in the table above.
Classify each runtime implementation using its actual behavior and evidence.

No Activity is currently classified **FULL PORT**. The absence of FULL PORT
entries is intentional: the GTK4 retirement gate must not be inferred from the
runtime matrix. A future port may move upward only when
its GTK3 behavior, object/persistence semantics, input, accessibility, and
normal user workflow are evidenced independently.

The runtime matrix remains useful and continues to report lifecycle coverage;
this ledger is the authoritative qualification boundary for Activity parity.

Evidence boundary: the current automated matrix waits for the Activity's
private D-Bus service, asks the shell to activate it, and calls `SetActive`
before requesting Stop. A PASS proves service readiness and clean process
termination; it still does not by itself prove a mapped surface, rendered
pixels, working pointer/keyboard input, persistence, or a usable replacement.
See `registry-repair-20260914.md` under `reports/gtk4` for the separate Clock
screenshot and the probe boundary.
