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

The GTK4 shell starts and renders Home at 1920×1080. Function-key probes sent
through the current QEMU monitor did not change the visible view, even after
the stale GTK3 shell process was stopped. This is now isolated as an input
delivery/ownership issue rather than a view-construction failure: direct
semantic D-Bus actions and pointer-driven GTK4 views remain available. The
next pass should instrument the guest keyboard device and verify whether the
monitor is targeting the active QEMU instance, then validate F1–F8 one key at a
time with event logs.
