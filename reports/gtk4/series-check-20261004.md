# GTK4 preview series-check correction

Date: 2026-10-04

The clean-series validator had fallen behind the build routing table after the
Activity sharing patches were added. It treated `0180`, `0181`, `0182`, and
`0185` as Sugar-shell patches even though the build applies them to
`sugar-toolkit-gtk4`; it also lacked the explicit Sugar routing entries for
`0183` and `0184`.

The validator now mirrors the build table. Host verification:

```text
466 passed
```
