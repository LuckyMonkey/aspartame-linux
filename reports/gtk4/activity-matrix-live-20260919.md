# GTK4 Activity launch matrix — 2026-09-19

Command run inside the live guest:

```sh
ACTIVITY_CYCLES=1 bash /mnt/aspartame-dev/scripts/sugar-gtk4-activity-matrix.sh
```

Result: **`activity-matrix=PASS`**.

All 50 registered modern bundles completed one real cycle with:

- `service-ready=PASS`
- `shell-active=PASS`
- launcher return `true`
- process and Activity ID observed
- `stop=(true,)`
- `cleanup=PASS`

The matrix covered Help, Count, Calculate, Clock, JAMClock, Image Viewer,
Terminal, Browse, Log, the Fructose game/learning set, and the remaining
bundled Activities through Read. This proves launch/runtime coverage and clean
normal stop behavior. It does **not** promote any row to FULL PORT or claim
feature, collaboration, accessibility, Journal, or visual parity; those remain
explicit per-Activity tasks in the launch ledger.

The modern AT-SPI bus pinning added to the Calculate and Help probes was also
used during this validation environment, where GTK3 and GTK4 Spaces were both
running.
