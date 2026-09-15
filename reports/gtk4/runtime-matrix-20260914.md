# GTK4 runtime matrix — 2026-09-14

Fresh evidence after the modern Home registry path and JAMClock/Clock ports.
The synchronized development share includes forty-nine modern bundles. A
fresh one-cycle matrix covered all 43 bundles registered at that point; Paint,
Diamond Fusion, Level, Moon, Get Books, and Jukebox then passed three direct
cycles (final Jukebox PID `460524`).

| Area | Evidence | Status |
| --- | --- | --- |
| GTK4 shell | `sugar-gtk4-runtime-check.sh gtk4` (desktop 1, pid `445246`) | PASS |
| Guest build | `sugar-gtk4-build.sh`, including patch 0015 | PASS |
| Home inventory | All forty-nine verified GTK4 bundles exposed through `SUGAR_ACTIVITIES_PATH` | PASS |
| Activity lifecycle | Full 43-bundle matrix (`425527` latest) plus direct three-cycle probes for Connect the Dots, Pippy, Paint, Diamond Fusion, Level, Moon, Get Books, and Jukebox | PASS: all matrix and direct cycles reported `cleanup=PASS` |
| Casilda | 232 real Journal launch/stop cycles across the three-cycle 41-bundle run, one-cycle 42/43-bundle rechecks, and direct probes | PASS |
| Spaces | semantic `sugar-gtk4-space.sh gtk3`, `gtk4`, and `status` round-trip | PASS: GTK3 pid `33761`, GTK4 pid `445246`, current workspace 1 |
| Physical F7/F8 | QMP and HMP injection | PARTIAL: no guest evdev events; semantic controller switching remains reliable |

Host regression suite: `pytest -q` → 207 passed (2026-09-14).

The GTK3 process remains separate and is not imported into the GTK4 process.
The full GTK4 replacement gate is still not claimed because physical input
transport, peer-backed collaboration, and the remaining legacy Activity catalog
are open.
