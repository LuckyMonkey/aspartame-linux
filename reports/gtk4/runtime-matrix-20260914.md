# GTK4 runtime matrix — 2026-09-14

Fresh evidence after the modern Home registry path and JAMClock/Clock ports.
The matrix was rerun from the synchronized development share; all twelve
modern bundles completed a live launch/stop cycle (latest Activity PIDs
`286366`–`286396`).

| Area | Evidence | Status |
| --- | --- | --- |
| GTK4 shell | `sugar-gtk4-runtime-check.sh gtk4` (desktop 1) | PASS |
| Guest build | `sugar-gtk4-build.sh`, including patch 0015 | PASS |
| Home inventory | All twelve verified GTK4 bundles exposed through `SUGAR_ACTIVITIES_PATH` | PASS |
| Activity lifecycle | Help, Count, Calculate, Clock, JAMClock, Image Viewer, Terminal, Browse, Log, Mastermind, Poll, Mancala (`286366`–`286396`) | PASS: every launch/stop reported `cleanup=PASS` |
| Casilda | Twelve real Journal launch/stop cycles | PASS |
| Physical F7/F8 | QMP and HMP injection | PARTIAL: no guest evdev events; semantic controller switching remains reliable |

The GTK3 process remains separate and is not imported into the GTK4 process.
The full GTK4 replacement gate is still not claimed because physical input
transport, peer-backed collaboration, and the remaining legacy Activity catalog
are open.
