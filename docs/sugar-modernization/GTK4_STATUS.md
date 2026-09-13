# GTK4 status

Status checked: 2026-09-13.

| Component | Aspartame now | Upstream GTK3 | Upstream GTK4 | Usable today? | Blocker / action |
|---|---|---|---|---|---|
| Sugar shell | Arch `sugar 0.121-7`, plus isolated GTK4 preview source | Working X11 shell | GTK4 preview shell starts in a separate process | GTK3 and GTK4 preview | Keep GTK3 stable; continue parity work in the modern Space |
| Toolkit | `sugar-toolkit-gtk3` package | Mature GTK3 API | `sugar-toolkit-gtk4` exists as a modern GTK4 toolkit | Toolkit experiments only | Consume upstream API; do not create `sugar5` locally |
| Artwork | Arch `sugar-artwork`, Sugar icon/theme paths | Working GTK3 theme | GTK4 asset integration is coupled to toolkit/shell ports | GTK3 only | Keep artwork ownership upstream-compatible |
| Datastore | Arch `sugar-datastore` | Working Carquinyol service | No independent GTK4 datastore requirement identified | Yes as a service | Keep D-Bus/service boundary stable |
| Fructose activities | Arch packages plus pinned bundled set | Mixed but runnable | Log launches through the GTK4 toolkit/Casilda boundary | Log lifecycle verified; broader set pending | Port one activity at a time, never mass-convert |
| Display/session | Xorg + Metacity + `sugar-runner` assumptions | Supported | Wayland/Casilda work is ongoing | X11 only | Treat Wayland as a separate backend experiment |
| Browse | GTK3/WebKitGTK-era Activity | GTK3 dependencies | GTK4/WebKitGTK 6 migration is activity-specific | GTK3 only | Do not make WebKitGTK4 a shell dependency |

Current preview checkpoint: GTK4 Home rendering, GTK3/GTK4 Spaces
switching, Sugar-styled palettes, a visible GTK4 Journal, and repeated Log
Activity launch/stop are verified in QEMU. The private datastore service and
metadata reader build are also verified. The modern Space now has top-level
F1--F6 semantic capture and starts as a real fullscreen 1920x1080 surface.
Pointer/keyboard delivery through the current QEMU synthetic-input harness,
full Journal interaction parity, and broader shell accessibility remain open
gates. Use
[GTK4_ACTIVITY_RUNBOOK.md](GTK4_ACTIVITY_RUNBOOK.md) for that sequence.

The GTK4 toolkit repository describes itself as a GTK4 toolkit and documents
`sugar4` APIs, while the main Sugar repository still documents GTK3 toolkit
dependencies. Sugar Labs' 2026 migration plan separates toolkit, shell,
Fructose, and Wayland work. Therefore the honest answer is: **GTK4 Sugar is
partially available, but a complete GTK4 Sugar desktop is not yet at the
parity gate**.

References:

- https://github.com/sugarlabs/sugar-toolkit-gtk4
- https://github.com/sugarlabs/sugar
- https://github.com/sugarlabs/GSoC/blob/master/Ideas-2026.md
- https://github.com/sugarlabs/sugar-runner
