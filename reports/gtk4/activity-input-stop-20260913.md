# GTK4 Activity input and stop probe — 2026-09-13

The modern Space launched the native `org.laptop.HelpActivity` bundle through
the Journal D-Bus service and returned `(true,)`.  The visible Casilda surface
was captured at [sugar-20260913-002106-v0.0.31.png](../screenshots/sugar-20260913-002106-v0.0.31.png).

Pointer focus and keyboard delivery were exercised against the real QEMU
window.  Typing into the Activity search field changed the GTK4 widget and
rendered `Input received: hj journal` in
[sugar-20260913-002117-v0.0.31.png](../screenshots/sugar-20260913-002117-v0.0.31.png).

The QEMU USB-tablet path then clicked the canonical top-right stop control.
The Help process disappeared, and the framebuffer returned to the stable GTK3
Home surface at [sugar-20260913-080643-v0.0.31.png](../screenshots/sugar-20260913-080643-v0.0.31.png).
The GTK4 shell remained alive; selecting the modern Space afterward passed:

```text
runtime-check=ok target=gtk4 pid=98527 desktop=1 window=0x1000518 stable_pid=100449 gtk4_pid=98527
```

This proves one real Activity map/input/stop cycle.  Repeated lifecycle and
physical F1–F8 delivery remain separate completion-gate items.
