# GTK4 Activity matrix

This matrix separates runtime coverage from behavioral parity. The lifecycle
probe proves that a registered bundle can launch through Journal/Casilda,
register its private Activity service, become active in the shell, and stop
without an orphan process. It does not by itself prove a complete port.

| Activities | Runtime coverage | Parity classification |
|---|---|---|
| Help, Count, Calculate, Clock, JAMClock, Image Viewer, Terminal, Browse, Log | 3-cycle Casilda launch/activate/stop evidence | FUNCTIONAL PORT (bounded workflows) |
| Write | 3-cycle launch plus UTF-8 Journal save/resume and save-failure cancellation/retry | FUNCTIONAL PORT |
| Read | 2-cycle launch plus seeded UTF-8 Journal object resume and visible page restoration | FUNCTIONAL PORT |
| Stopwatch | 2-cycle launch plus seeded JSON Journal object resume and visible elapsed-time restoration | FUNCTIONAL PORT |
| Calculate | 2-cycle launch plus seeded Journal expression resume and visible result restoration | FUNCTIONAL PORT |
| Level | 2-cycle launch plus seeded JSON Journal inclination resume and visible readout restoration | FUNCTIONAL PORT |
| Markdown | 2-cycle launch plus seeded UTF-8 Journal source resume and visible editor restoration | FUNCTIONAL PORT |
| Finance | 2-cycle launch plus seeded JSON transaction resume and visible balance restoration | FUNCTIONAL PORT |
| Words | 2-cycle launch plus seeded JSON word resume and visible lookup restoration | FUNCTIONAL PORT |
| Portfolio | 2-cycle launch plus seeded JSON title/body resume and visible title restoration | FUNCTIONAL PORT |
| Jukebox | 2-cycle launch plus seeded JSON playlist resume and visible track restoration | FUNCTIONAL PORT |
| Grid Paint | 2-cycle launch plus seeded JSON cell-selection resume and visible summary restoration | FUNCTIONAL PORT |
| Abacus | 2-cycle launch plus seeded JSON rod-value resume and visible value restoration | FUNCTIONAL PORT |
| Pippy | 2-cycle launch plus seeded UTF-8 source resume and visible editor restoration | FUNCTIONAL PORT |
| Paint | 2-cycle launch plus seeded JSON stroke/color resume and visible status restoration | FUNCTIONAL PORT |
| FotoToon | 2-cycle launch plus seeded JSON caption-canvas resume and visible caption restoration | FUNCTIONAL PORT |
| Mastermind, Poll, Mancala, Reversi, Jumble, NumberRush, Across and Down, IQ, Appel Haken, BallAndBrick, Implode, PlayGo, BlockParty, Typing Turtle, Memorize, Maze, Last One Loses, Gears, TurtleBlocks, Game Of Life, Color My World, Planets, Connect the Dots, Diamond Fusion, Level, Moon, Get Books | 3-cycle matrix evidence | COVERAGE IMPLEMENTATION |
| Get Things Done | 2-cycle launch plus seeded JSON Journal task-list resume and clean stop | FUNCTIONAL PORT |

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
highest-value parity work is peer-backed Neighborhood behavior, physical input
delivery below the QEMU transport, and continued per-Activity parity promotion.
