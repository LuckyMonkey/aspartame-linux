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

## Historical runtime frontier

The GTK4 shell starts and renders Home at 1920×1080. The original HMP
`sendkey` helper targeted the wrong input path; it has been replaced with QMP
`input-send-event` events for the configured USB keyboard. The guest log now
records `GTK4 semantic key event: F5`, proving delivery to the GTK4 process.

At the time of this report, the F5 Journal action exposed a datastore
disconnect while querying metadata. That issue was subsequently resolved by
the native Journal surface and is covered by the current Journal
search/resume evidence and the 41-Activity lifecycle matrix. The remaining
function-key limitation is transport-level: QMP/HMP injections do not produce
guest evdev events, while semantic Space switching remains reliable.
