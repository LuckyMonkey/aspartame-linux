# GTK4 status

Status checked: 2026-09-14.

| Component | Aspartame now | Upstream GTK3 | Upstream GTK4 | Usable today? | Blocker / action |
|---|---|---|---|---|---|
| Sugar shell | Arch `sugar 0.121-7`, plus isolated GTK4 preview source | Working X11 shell | GTK4 preview shell starts in a separate process | GTK3 and GTK4 preview | Keep GTK3 stable; compare behavior in the modern Space |
| Toolkit | GTK3 and GTK4 toolkits remain separate | Mature GTK3 API | `sugar-toolkit-gtk4` `sugar4` APIs | GTK4 shell usable | Keep GTK3/GTK4 out of one GI process |
| Artwork | Arch `sugar-artwork`, normalized icon pipeline | Working GTK3 theme | GTK4 renderer consumes activity metadata/XOColor semantics | GTK3 and GTK4 preview | Keep artwork ownership upstream-compatible |
| Datastore | Arch `sugar-datastore` | Working Carquinyol service | No independent GTK4 datastore requirement identified | Yes as a service | Keep D-Bus/service boundary stable |
| Fructose activities | Arch packages plus pinned bundled set | Mixed but runnable | Help and Log launch through the GTK4 toolkit/Casilda boundary | Individual GTK4 ports verified | Port one activity at a time, never mass-convert |
| Display/session | Xorg + Metacity + `sugar-runner` assumptions | Supported | Casilda owns the private Activity surface inside the GTK4 preview | GTK4 preview on X11 host | Keep the Casilda boundary; do not claim a full Wayland session |
| Calculate | GTK3 Activity | Native GTK4 bundle | Safe arithmetic editor registered in the modern prefix | GTK4 verified 2026-09-14 | `org.aspartame.Calculate` launches through Journal and stops cleanly |
| Image Viewer | GTK3 Activity | Pinned GTK4 source | Registered from the GTK4 port without shell changes | GTK4 verified 2026-09-14 | `org.laptop.ImageViewerActivity` launches and stops cleanly |
| Terminal | GTK3 Activity | Pinned GTK4 source + guest `vte4` | Registered once the GTK4 Vte typelib is available | GTK4 verified 2026-09-14 | `org.laptop.Terminal` launches and stops cleanly |
| Browse | GTK4 source is pinned | Guest `webkitgtk-6.0` installed | Activity-specific dependency; kept out of the shell build | GTK4 verified 2026-09-14 | `org.laptop.WebActivity` launches and stops cleanly; repeated lifecycle is recorded |

Current verified checkpoint: GTK4 Home Favorites/List/search, Frame,
Journal search/resume/edit/selection, Settings navigation,
Neighborhood/Group empty states, Sugar palettes, clipboard transfer, Help,
Activity Manager policy, and repeated normal/abnormal Activity launch-stop
cleanup run in the modern Space. Native Journal and Home List launch paths
have real Casilda Activity-surface and process evidence. The complete matrix
is maintained in `reports/gtk4/runtime-matrix-20260913.md`.

Remaining limits are explicit: physical F1-F6 delivery is below the current
QEMU/evdev transport; Neighborhood collaboration cannot be exercised without
peers; and unsupported GTK3-only Activities such as Browse remain individual
porting targets. These are not silently counted as GTK4 parity.

The GTK4 toolkit repository describes itself as a GTK4 toolkit and documents
`sugar4` APIs, while the main Sugar repository still documents GTK3 toolkit
dependencies. Aspartame therefore keeps the stable GTK3 Space as a behavioral
reference while operating a separately tested GTK4 preview Space. The preview
is materially usable, but the full completion gate is not claimed because the
physical function-key transport, peer collaboration, and complete Activity
catalog remain open.

References:

- https://github.com/sugarlabs/sugar-toolkit-gtk4
- https://github.com/sugarlabs/sugar
- https://github.com/sugarlabs/GSoC/blob/master/Ideas-2026.md
- https://github.com/sugarlabs/sugar-runner
