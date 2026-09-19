# GTK4 Activity matrix — 2026-09-19

After the full guest rebuild at commit `289e64d`, the development guest ran:

```text
ACTIVITY_CYCLES=1 ./scripts/sugar-gtk4-activity-matrix.sh
```

Result:

```text
registered bundles exercised: 50
service-ready/active/stop/cleanup passes: 50
activity-matrix=PASS
```

Every row launched a fresh Activity process through the Journal D-Bus launch
contract, waited for its private Activity service, activated it through the
shell, requested stop, and verified process cleanup. The matrix covered Help,
Count, Calculate, Clock, JAMClock, Image Viewer, Terminal, Browse, Log, the
native game/learning ports, Write, Read, Jukebox, Get Books, and the remaining
registered GTK4 coverage implementations.

This is runtime coverage evidence. It does not promote any Activity to FULL
PORT: the authoritative classification remains
`docs/sugar-modernization/ACTIVITY_PORT_CLASSIFICATION.md`, where behavioral
scope, persistence breadth, input, accessibility, and collaboration limits
are recorded separately.
