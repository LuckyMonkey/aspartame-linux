# GTK4 runtime matrix — 2026-09-14

Fresh evidence after the modern Home registry path and JAMClock/Clock ports.
The synchronized development share includes forty-two modern bundles. A fresh
one-cycle matrix completed a launch/stop cycle for every registered bundle;
Connect the Dots also passed three direct cycles (final PID `417017`).

| Area | Evidence | Status |
| --- | --- | --- |
| GTK4 shell | `sugar-gtk4-runtime-check.sh gtk4` (desktop 1, pid `265471`) | PASS |
| Guest build | `sugar-gtk4-build.sh`, including patch 0015 | PASS |
| Home inventory | All forty-two verified GTK4 bundles exposed through `SUGAR_ACTIVITIES_PATH` | PASS |
| Activity lifecycle | Full 42-bundle matrix (`418418` latest) plus Connect the Dots direct cycles | PASS: all 42 matrix cycles and 3 direct cycles reported `cleanup=PASS` |
| Casilda | 165 real Journal launch/stop cycles across the three-cycle 41-bundle run, one-cycle 42-bundle recheck, and direct Connect the Dots probe | PASS |
| Spaces | semantic `sugar-gtk4-space.sh gtk3`, `gtk4`, and `status` round-trip | PASS: GTK3 pid `33761`, GTK4 pid `265471`, current workspace 1 |
| Physical F7/F8 | QMP and HMP injection | PARTIAL: no guest evdev events; semantic controller switching remains reliable |

Host regression suite: `pytest -q` → 207 passed (2026-09-14).

The GTK3 process remains separate and is not imported into the GTK4 process.
The full GTK4 replacement gate is still not claimed because physical input
transport, peer-backed collaboration, and the remaining legacy Activity catalog
are open.
