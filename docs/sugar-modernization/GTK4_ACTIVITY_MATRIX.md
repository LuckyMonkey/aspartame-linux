# GTK4 Activity matrix

This matrix separates runtime coverage from behavioral parity. The lifecycle
probe proves that a registered bundle can launch through Journal/Casilda,
register its private Activity service, become active in the shell, and stop
without an orphan process. It does not by itself prove a complete port.

| Activities | Runtime coverage | Parity classification |
|---|---|---|
| Help, Count, Calculate, Clock, JAMClock, Image Viewer, Terminal, Browse, Log | 3-cycle Casilda launch/activate/stop evidence | FUNCTIONAL PORT (bounded workflows) |
| Write | 3-cycle launch plus UTF-8 Journal save/resume and save-failure cancellation/retry | FUNCTIONAL PORT |
| Read | 2-cycle launch/activate/stop; Journal UTF-8 hooks compile in guest | COVERAGE IMPLEMENTATION (live resume pending) |
| Mastermind, Poll, Mancala, Reversi, Jumble, NumberRush, Across and Down, IQ, Appel Haken, BallAndBrick, Implode, PlayGo, BlockParty, Typing Turtle, Memorize, Maze, FotoToon, Portfolio, Markdown, Finance, Words, Last One Loses, Get Things Done, Grid Paint, Stopwatch, Gears, TurtleBlocks, Game Of Life, Color My World, Abacus, Planets, Connect the Dots, Pippy, Paint, Diamond Fusion, Level, Moon, Get Books, Jukebox | 3-cycle matrix evidence | COVERAGE IMPLEMENTATION |

The authoritative class definitions and per-Activity boundaries live in
[`ACTIVITY_PORT_CLASSIFICATION.md`](ACTIVITY_PORT_CLASSIFICATION.md). No
Activity is currently a FULL PORT, and no implemented bundle is being counted
as a PLACEHOLDER merely because it has reduced behavior.

## Porting gate

Use [GTK4_ACTIVITY_RUNBOOK.md](GTK4_ACTIVITY_RUNBOOK.md) for each Activity.
Promotion requires evidence appropriate to the claimed class:

- import/build at the pinned source state;
- Home activation in the running GTK4 preview;
- private Activity D-Bus service and intended surface path;
- real input and accessible controls for the claimed workflow;
- canonical Stop action, process exit, and bus-name release;
- Journal relaunch/resume when the Activity owns persistent state;
- comparison with the stable GTK3 behavior before claiming parity.

The full matrix is a coverage instrument, not a retirement gate. The remaining
highest-value parity work is live Read/Stopwatch object resume, peer-backed
Neighborhood behavior, and physical input delivery below the QEMU transport.
