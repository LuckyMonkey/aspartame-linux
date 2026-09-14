# GTK4 runtime matrix — 2026-09-14

Fresh evidence after the modern Home registry path and JAMClock/Clock ports.
The synchronized development share now includes thirty-seven modern bundles. A
fresh full matrix completed three cycles for every registered bundle before the
latest addition; Game Of Life has a separate three-cycle probe ending at PID
`390403`.

| Area | Evidence | Status |
| --- | --- | --- |
| GTK4 shell | `sugar-gtk4-runtime-check.sh gtk4` (desktop 1, pid `265471`) | PASS |
| Guest build | `sugar-gtk4-build.sh`, including patch 0015 | PASS |
| Home inventory | All thirty-seven verified GTK4 bundles exposed through `SUGAR_ACTIVITIES_PATH` | PASS |
| Activity lifecycle | Full 35-bundle matrix (`384832` latest), TurtleBlocks (`387729`), and Game Of Life (`390403`) | PASS: all 111 recorded launch/stop cycles reported `cleanup=PASS` |
| Casilda | 111 real Journal launch/stop cycles (three per registered Activity) | PASS |
| Spaces | semantic `sugar-gtk4-space.sh gtk3`, `gtk4`, and `status` round-trip | PASS: GTK3 pid `33761`, GTK4 pid `265471`, current workspace 1 |
| Physical F7/F8 | QMP and HMP injection | PARTIAL: no guest evdev events; semantic controller switching remains reliable |

Host regression suite: `pytest -q` → 201 passed (2026-09-14).

The GTK3 process remains separate and is not imported into the GTK4 process.
The full GTK4 replacement gate is still not claimed because physical input
transport, peer-backed collaboration, and the remaining legacy Activity catalog
are open.
