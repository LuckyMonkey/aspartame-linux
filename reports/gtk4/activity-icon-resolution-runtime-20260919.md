# Activity icon runtime check — 2026-09-19

The rebuilt modern Space was switched to the native Home List view through
`org.laptop.Shell.ShowList`. A fresh 1920×1080 capture shows the installed
Activity list with visible artwork for Abacus, Across and Down, Appel Haken,
BallAndBrick, BlockParty, Browse, Calculate, Clock, Color My World, Count,
Diamond Fusion, Finance, FotoToon, and the other visible rows.

- Screenshot: `reports/screenshots/sugar-20260919-125502-v0.0.31.png`
- SHA-256: `aeeed2ca5885407cdee865852d461bd6d5767ca3b737d9a07b3d192c8a654488`
- Resolution: 1920×1080
- Home status: `54 installed activities`
- State labels: visible rows report `Stopped`; unsupported legacy entries are
  explicitly labeled `Classic Space activity`.

This validates the shared metadata → icon renderer path in the live GTK4
shell. The duplicate display name for native and legacy Calculate is a
registry/catalog presentation decision, not an icon-loading failure; it is
queued separately rather than hidden by a visual workaround.
