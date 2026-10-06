# Color My World GTK4 UX pass — 2026-10-06

Color My World was rebuilt from the current GTK4 preview tree and captured
through the real Journal launch route in a headless QEMU guest.

The visual driver initially produced misleading Home screenshots because its
root-controlled `runuser` call did not pass the guest X11 session's
`XAUTHORITY`. The driver now preserves `DISPLAY`, `XAUTHORITY`, and
`XDG_RUNTIME_DIR` when selecting the modern Space. A targeted capture with a
10-second compositor settle then produced the activity surface:

```text
visual-sweep=COMPLETE pass=1 fail=0 resolution=1920x1080
```

The reviewed frame shows:

- a full-size activity surface below the Sugar toolbar;
- clear title and instruction hierarchy;
- a labeled, expandable map canvas with Greenland, North America, South
  America, Europe, Africa, Asia, SE Asia, and Australia;
- a centered palette with five named color buttons;
- a visible `Clear map` action and a status line for the current selection.

The map is intentionally a compact offline region model rather than finished
cartographic artwork. The UX is now usable and legible; replacing the
rectangular region geometry with richer artwork remains a later content pass,
not a GTK3 fallback requirement.

The activity lifecycle roundtrip also passed resume, service release, and
shell cleanup. Full-parity retirement evidence remains open for Color My World
and the other activities listed by the retirement gate.
