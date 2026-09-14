# GTK4 runtime matrix — 2026-09-14

Fresh evidence after the modern Home registry path and JAMClock/Clock ports:

| Area | Evidence | Status |
| --- | --- | --- |
| GTK4 shell | `sugar-gtk4-runtime-check.sh gtk4` (`pid=265471`, desktop 1) | PASS |
| Guest build | `sugar-gtk4-build.sh`, including patch 0015 | PASS |
| Home inventory | All nine verified GTK4 bundles exposed through `SUGAR_ACTIVITIES_PATH` | PASS |
| Activity lifecycle | Help, Count, Calculate, Clock, JAMClock, Image Viewer, Terminal, Browse, Log | PASS: every launch/stop reported `cleanup=PASS` |
| Casilda | Nine real Journal launch/stop cycles | PASS |
| Physical F7/F8 | QMP and HMP injection | PARTIAL: no guest evdev events; semantic controller switching remains reliable |

The GTK3 process remains separate and is not imported into the GTK4 process.
The full GTK4 replacement gate is still not claimed because physical input
transport, peer-backed collaboration, and the remaining legacy Activity catalog
are open.
