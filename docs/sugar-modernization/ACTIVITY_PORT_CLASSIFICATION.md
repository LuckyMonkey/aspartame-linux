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
| Read | COVERAGE IMPLEMENTATION | GTK4 reader now accepts UTF-8 Journal objects as form-feed-separated pages; live object resume and format breadth are not yet evidenced |
| Write | FUNCTIONAL PORT | UTF-8 text editing, Journal save/stop/resume, and save-failure cancellation/retry verified with real GTK4 Activity processes on 2026-09-15; rich text and upstream document-format parity remain absent |
| Mastermind, Poll, Mancala, Reversi, Jumble, NumberRush | COVERAGE IMPLEMENTATION | Native playable cores used to exercise GTK4 input/render/lifecycle |
| Across and Down, IQ, Appel Haken, BallAndBrick, Implode, PlayGo, BlockParty | COVERAGE IMPLEMENTATION | Native puzzle/game cores; upstream feature parity not established |
| Typing Turtle, Memorize, Maze, FotoToon, Portfolio, Markdown, Finance, Words | COVERAGE IMPLEMENTATION | Native task surfaces; reduced from original feature sets |
| Last One Loses, Get Things Done, Grid Paint, Stopwatch, Gears, TurtleBlocks | COVERAGE IMPLEMENTATION | Native interaction cores; Stopwatch now has a Journal elapsed-time payload, but persistence/collaboration parity is not established |
| Game Of Life, Color My World, Abacus, Planets | COVERAGE IMPLEMENTATION | Native rendering/interaction cores; not full upstream replacements |
| Connect the Dots, Pippy, Paint, Diamond Fusion, Level, Moon | COVERAGE IMPLEMENTATION | Bounded native demos proving distinct GTK4 activity paths |
| Get Books, Jukebox | COVERAGE IMPLEMENTATION | Offline catalog/playlist surfaces; network/media-library parity not claimed |

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
