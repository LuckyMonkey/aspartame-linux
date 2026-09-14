# GTK4 runtime matrix — 2026-09-14

Fresh evidence after the modern Home registry path and JAMClock/Clock ports.
The synchronized development share now includes thirty-one modern bundles; the
latest direct three-cycle probe ended with Last One Loses PID `365732`.

| Area | Evidence | Status |
| --- | --- | --- |
| GTK4 shell | `sugar-gtk4-runtime-check.sh gtk4` (desktop 1) | PASS |
| Guest build | `sugar-gtk4-build.sh`, including patch 0015 | PASS |
| Home inventory | All thirty-one verified GTK4 bundles exposed through `SUGAR_ACTIVITIES_PATH` | PASS |
| Activity lifecycle | Help, Count, Calculate, Clock, JAMClock, Image Viewer, Terminal, Browse, Log, Mastermind, Poll, Mancala, Reversi, Jumble, Number Rush, Across and Down, IQ, Appel Haken, BallAndBrick, Implode, PlayGo, BlockParty, Typing Turtle, Memorize, Maze, FotoToon, Portfolio, Markdown, Finance, Words, Last One Loses (`365732` latest) | PASS: Last One Loses direct cycles reported `cleanup=PASS`; prior matrix covered 78 cycles |
| Casilda | Last One Loses direct three-cycle launch/stop probe | PASS |
| Physical F7/F8 | QMP and HMP injection | PARTIAL: no guest evdev events; semantic controller switching remains reliable |

Host regression suite: `pytest -q` → 186 passed (2026-09-14).

The GTK3 process remains separate and is not imported into the GTK4 process.
The full GTK4 replacement gate is still not claimed because physical input
transport, peer-backed collaboration, and the remaining legacy Activity catalog
are open.
