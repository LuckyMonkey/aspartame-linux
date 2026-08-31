# GTK4 status

Status checked: 2026-08-31.

| Component | Aspartame now | Upstream GTK3 | Upstream GTK4 | Usable today? | Blocker / action |
|---|---|---|---|---|---|
| Sugar shell | Arch `sugar 0.121-7`, tracked GTK3 overlay | Working X11 shell | Shell migration is still roadmap/PR work | GTK3 only | Keep stable; test upstream shell work in isolation |
| Toolkit | `sugar-toolkit-gtk3` package | Mature GTK3 API | `sugar-toolkit-gtk4` exists as a modern GTK4 toolkit | Toolkit experiments only | Consume upstream API; do not create `sugar5` locally |
| Artwork | Arch `sugar-artwork`, Sugar icon/theme paths | Working GTK3 theme | GTK4 asset integration is coupled to toolkit/shell ports | GTK3 only | Keep artwork ownership upstream-compatible |
| Datastore | Arch `sugar-datastore` | Working Carquinyol service | No independent GTK4 datastore requirement identified | Yes as a service | Keep D-Bus/service boundary stable |
| Fructose activities | Arch packages plus pinned bundled set | Mixed but runnable | Calculate/Log and others are active migration targets | Individual GTK4 ports only | Port one activity at a time, never mass-convert |
| Display/session | Xorg + Metacity + `sugar-runner` assumptions | Supported | Wayland/Casilda work is ongoing | X11 only | Treat Wayland as a separate backend experiment |
| Browse | GTK3/WebKitGTK-era Activity | GTK3 dependencies | GTK4/WebKitGTK 6 migration is activity-specific | GTK3 only | Do not make WebKitGTK4 a shell dependency |

The GTK4 toolkit repository describes itself as a GTK4 toolkit and documents
`sugar4` APIs, while the main Sugar repository still documents GTK3 toolkit
dependencies. Sugar Labs' 2026 migration plan separates toolkit, shell,
Fructose, and Wayland work. Therefore the honest answer is: **GTK4 Sugar is
partially available, but a complete GTK4 Sugar desktop is not yet a supported
Aspartame runtime**.

References:

- https://github.com/sugarlabs/sugar-toolkit-gtk4
- https://github.com/sugarlabs/sugar
- https://github.com/sugarlabs/GSoC/blob/master/Ideas-2026.md
- https://github.com/sugarlabs/sugar-runner
