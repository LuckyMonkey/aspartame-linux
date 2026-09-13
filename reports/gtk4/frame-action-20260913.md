# GTK4 Frame semantic action — 2026-09-13

Environment: Aspartame QEMU guest, GTK4 Space, GTK 4.22.4, Casilda 1.5.0,
1920x1080 display.

The rebuilt GTK4 shell was restarted after applying preview patches 0052–0054.
Calling `org.laptop.Shell.ShowFrame` on `/org/laptop/Shell` returned boolean
`true`. The resulting capture visibly shows the native Sugar Frame overlay:
top zoom/activity controls, edge navigation controls, active Activity state,
and the bottom device/clipboard tray over the Home surface.

Evidence screenshot: `reports/screenshots/sugar-20260912-203401-v0.0.31.png`.

This validates Frame construction/reveal through the GTK4 shell process rather
than the GTK3 global key grab. Physical F6 delivery through the current QEMU
synthetic-input path remains separately unverified.
