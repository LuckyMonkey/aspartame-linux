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
| Calculate | FUNCTIONAL PORT | Safe arithmetic editor; not a claim of full upstream feature parity |
| Clock | FUNCTIONAL PORT | Native time/date presentation |
| JAMClock | FUNCTIONAL PORT | Native time/date replacement under the original identity |
| Image Viewer | FUNCTIONAL PORT | Native image surface through the pinned bundle path |
| Terminal | FUNCTIONAL PORT | Native VTE terminal path; terminal feature parity remains bounded |
| Browse | FUNCTIONAL PORT | Native WebKit path; collaboration/download parity is not claimed |
| Log | FUNCTIONAL PORT | Native log list surface |
| Read | FUNCTIONAL PORT | UTF-8 Journal text object resume, visible page restoration, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; PDF/EPUB/format breadth and upstream Read parity remain absent |
| Write | FUNCTIONAL PORT | UTF-8 text editing, Journal save/stop/resume, and save-failure cancellation/retry verified with real GTK4 Activity processes on 2026-09-15; rich text and upstream document-format parity remain absent |
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
| Typing Turtle, FotoToon, Portfolio, Words | COVERAGE IMPLEMENTATION | Native task surfaces; reduced from original feature sets |
| Maze | FUNCTIONAL PORT | Four-direction movement, direct cell selection, JSON Journal position resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full maze generation and collaboration breadth remain absent |
| Memorize | FUNCTIONAL PORT | Card reveal/matching workflow, JSON Journal card/match resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full randomization, scoring, and collaboration breadth remain absent |
| Words | FUNCTIONAL PORT | UTF-8 word entry, lookup result, and JSON Journal save/resume verified with real GTK4 Activity processes on 2026-09-15; translation/audio breadth remains absent |
| Portfolio | FUNCTIONAL PORT | UTF-8 project title/body editing and JSON Journal save/resume verified with real GTK4 Activity processes on 2026-09-15; rich media/export breadth remains absent |
| FotoToon | FUNCTIONAL PORT | Caption canvas interaction and JSON Journal save/resume verified with real GTK4 Activity processes on 2026-09-15; image import/layout breadth remains absent |
| Finance | FUNCTIONAL PORT | Income/expense tracking, balance calculation, and JSON Journal save/resume verified with real GTK4 Activity processes on 2026-09-15; charts, import/export, and collaboration remain absent |
| Markdown | FUNCTIONAL PORT | UTF-8 Markdown editing, live preview, and Journal save/resume verified with real GTK4 Activity processes on 2026-09-15; full parser/rendering parity remains absent |
| Stopwatch | FUNCTIONAL PORT | JSON Journal elapsed-time resume, visible time restoration, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; lap/export/collaboration breadth is not claimed |
| Grid Paint, TurtleBlocks | COVERAGE IMPLEMENTATION | Native interaction cores; full upstream parity is not established |
| Gears | FUNCTIONAL PORT | Native gear rendering/rotation controls, visible rotation state, JSON Journal phase resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; animation and collaboration breadth remain absent |
| Last One Loses | FUNCTIONAL PORT | Take-away turn workflow, visible token count, JSON Journal pile resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; strategy/AI and collaboration breadth remain absent |
| Grid Paint | FUNCTIONAL PORT | 10×10 cell painting, selection summary, and JSON Journal save/resume verified with real GTK4 Activity processes on 2026-09-15; advanced layer/fill tools remain absent |
| Get Things Done | FUNCTIONAL PORT | Native task list with add/complete controls and JSON Journal save/resume verified with real GTK4 Activity processes on 2026-09-15; collaboration and upstream feature breadth remain absent |
| Game Of Life, Color My World, Abacus, Planets | COVERAGE IMPLEMENTATION | Native rendering/interaction cores; not full upstream replacements |
| Abacus | FUNCTIONAL PORT | Place-value rod controls, computed value, and JSON Journal save/resume verified with real GTK4 Activity processes on 2026-09-15; advanced bead manipulation remains absent |
| Planets | FUNCTIONAL PORT | Planet selection, orbit canvas, and JSON Journal selection resume verified with real GTK4 Activity processes on 2026-09-15; full simulation breadth remains absent |
| Color My World | FUNCTIONAL PORT | Palette selection, rendered swatch, and JSON Journal color resume verified with real GTK4 Activity processes on 2026-09-15; full artwork/collaboration breadth remains absent |
| Game Of Life | FUNCTIONAL PORT | Finite-grid stepping, live-cell selection, generation summary, and JSON Journal resume verified with real GTK4 Activity processes on 2026-09-15; advanced patterns/collaboration remain absent |
| Pippy, Paint, Diamond Fusion, Moon | COVERAGE IMPLEMENTATION | Bounded native demos proving distinct GTK4 activity paths |
| Connect the Dots | FUNCTIONAL PORT | Numbered point selection, visible connection progress, JSON Journal progress resume, and clean stop were verified with real GTK4 Activity processes on 2026-09-15; full artwork and collaboration breadth remain absent |
| Pippy | FUNCTIONAL PORT | UTF-8 Python source editing, isolated execution surface, and Journal save/resume verified with real GTK4 Activity processes on 2026-09-15; full upstream editor/runtime breadth remains absent |
| Typing Turtle | FUNCTIONAL PORT | Keyboard exercise progression and JSON Journal exercise-index resume verified with real GTK4 Activity processes on 2026-09-15; scoring/audio breadth remains absent |
| Moon | FUNCTIONAL PORT | Phase selection, rendered moon view, and JSON Journal phase resume verified with real GTK4 Activity processes on 2026-09-15; full astronomical simulation remains absent |
| Paint | FUNCTIONAL PORT | Pointer stroke drawing, color selection, and JSON Journal save/resume verified with real GTK4 Activity processes on 2026-09-15; image layers/tools remain absent |
| Level | FUNCTIONAL PORT | Offline inclination controls, drag interaction, and JSON Journal resume verified with real GTK4 Activity processes on 2026-09-15; hardware sensor integration remains outside this claim |
| Get Books, Jukebox | COVERAGE IMPLEMENTATION | Offline catalog/playlist surfaces; network/media-library parity not claimed |
| Jukebox | FUNCTIONAL PORT | Offline playlist selection, local-track metadata, and JSON Journal save/resume verified with real GTK4 Activity processes on 2026-09-15; codec/media playback parity remains absent |
| Get Books | FUNCTIONAL PORT | Offline catalog search, selected-book metadata, and JSON Journal query/selection resume verified with real GTK4 Activity processes on 2026-09-15; network catalogs/downloads remain absent |

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
