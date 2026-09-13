# Repeated GTK4 Activity lifecycle — 2026-09-13

After the StopActivity implementation, two complete live cycles were run in
the GTK4 Space (shell PID `55327`):

| cycle | launch | child | stop | result |
| --- | --- | --- | --- | --- |
| 1 | Journal D-Bus `true` | 55603 | Shell D-Bus `true` | `/proc/55603` absent |
| 2 | Journal D-Bus `true` | 55639 | Shell D-Bus `true` | `/proc/55639` absent |

The shell remained alive after both cycles. The root cause of the prior
no-reply race was synchronous self-D-Bus notification from the toolkit child
watch. Patch `0066` now calls `shell.get_model().notify_launch_failed()`
locally instead of synchronously calling the shell service over D-Bus.

Additional visual stop probe: Help was visible, `StopActivity` returned
`true`, PID `55673` disappeared, and the following 1920×1080 capture showed
the Home favorites ring with no Help surface or stale Help window:
`reports/screenshots/sugar-20260912-220348-v0.0.31.png`.
