# GTK4 function-key frontier — 2026-09-13

The guest preview rebuild now advances through patch `0015` and applies the
semantic Journal canvas reparenting patch `0079`.

## Verified

- Full `scripts/sugar-gtk4-build.sh`: PASS (toolkit, Casilda, sugar-ext,
  Jarabe, datastore).
- `0079-journal-safe-canvas-reparent.patch`: applied/verified.
- `0080-main-focusable-key-surface.patch`: applied/verified; the GTK4 overlay
  is explicitly focusable before the window focus is assigned.
- Guest source contains `_overlay.set_focusable(True)`.

## Runtime frontier

The GTK4 shell starts and renders Home at 1920×1080. The original HMP
`sendkey` helper targeted the wrong input path; it has been replaced with QMP
`input-send-event` events for the configured USB keyboard. The guest log now
records `GTK4 semantic key event: F5`, proving delivery to the GTK4 process.

The F5 Journal action then exposes a separate datastore failure (the service
disconnects while querying metadata), so the next pass should repair that
service boundary and validate F1–F8 one key at a time with event logs and
screenshots.
