# GTK4 runtime matrix — 2026-09-14

Fresh evidence after the modern Home registry path and JAMClock/Clock ports.
The synchronized development share now includes thirty-five modern bundles. A
fresh full matrix completed three cycles for every registered bundle before the
latest addition; Gears has a separate three-cycle probe ending at PID
`381858`.

| Area | Evidence | Status |
| --- | --- | --- |
| GTK4 shell | `sugar-gtk4-runtime-check.sh gtk4` (desktop 1) | PASS |
| Guest build | `sugar-gtk4-build.sh`, including patch 0015 | PASS |
| Home inventory | All thirty-five verified GTK4 bundles exposed through `SUGAR_ACTIVITIES_PATH` | PASS |
| Activity lifecycle | Full 33-bundle matrix (`376518` latest), Stopwatch (`379186`), and Gears (`381858`) | PASS: all 105 recorded launch/stop cycles reported `cleanup=PASS` |
| Casilda | 105 real Journal launch/stop cycles (three per registered Activity) | PASS |
| Physical F7/F8 | QMP and HMP injection | PARTIAL: no guest evdev events; semantic controller switching remains reliable |

Host regression suite: `pytest -q` → 186 passed (2026-09-14).

The GTK3 process remains separate and is not imported into the GTK4 process.
The full GTK4 replacement gate is still not claimed because physical input
transport, peer-backed collaboration, and the remaining legacy Activity catalog
are open.
