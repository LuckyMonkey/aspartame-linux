# GTK4 runtime matrix — 2026-09-14

Fresh evidence after the modern Home registry path and JAMClock/Clock ports.
The synchronized development share now includes sixteen modern bundles; the
complete matrix remains green with three-cycle probes. The latest full run
ended with Across and Down PID `311966`.

| Area | Evidence | Status |
| --- | --- | --- |
| GTK4 shell | `sugar-gtk4-runtime-check.sh gtk4` (desktop 1) | PASS |
| Guest build | `sugar-gtk4-build.sh`, including patch 0015 | PASS |
| Home inventory | All sixteen verified GTK4 bundles exposed through `SUGAR_ACTIVITIES_PATH` | PASS |
| Activity lifecycle | Help, Count, Calculate, Clock, JAMClock, Image Viewer, Terminal, Browse, Log, Mastermind, Poll, Mancala, Reversi, Jumble, Number Rush, Across and Down (`311966` latest) | PASS: all 48 launch/stop cycles reported `cleanup=PASS` |
| Casilda | 48 real Journal launch/stop cycles (three per Activity) | PASS |
| Physical F7/F8 | QMP and HMP injection | PARTIAL: no guest evdev events; semantic controller switching remains reliable |

Host regression suite: `pytest -q` → 181 passed.

The GTK3 process remains separate and is not imported into the GTK4 process.
The full GTK4 replacement gate is still not claimed because physical input
transport, peer-backed collaboration, and the remaining legacy Activity catalog
are open.
