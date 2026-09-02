# GTK4 component matrix

| Component | Upstream head used | Aspartame state | Arch status | Blocker/action |
|---|---|---|---|---|
| Sugar shell | official PR #1106, `f84a2d5` | staged isolated runtime | Home/search/return stable beyond 60 seconds | register one GTK4 Activity, then prove lifecycle |
| sugar-toolkit-gtk4 | official PR #35, `74f6a05` | editable isolated venv | imports; 55 targeted tests pass; renderer scroll contract restored | upstream patches `0018` and `0020` |
| sugar-ext | main, `563760e` | installed in isolated prefix | build and 5 native tests pass | upstream gtk-doc correction candidate |
| sugar-artwork | main, `3c4854d` | pinned checkout | not installed | shell integration |
| datastore | main, `7aa97e7` | native reader built; private service runs | stable D-Bus contract verified | preserve API while porting Journal |
| Casilda | main, `cecb869` | 1.5.0 installed in isolated prefix | `wayland-sugar` and protocols verified | output reports 0x0 until an embedded surface is allocated |
| Calculate/Log/Browse/ImageViewer/Terminal | pinned migration heads | source only | not installed | test one activity at a time |

The shell/toolkit rows are fetched from sugarlabs/* pull-request refs, not
contributor-fork branch names. This keeps the preview connected to the actual
review objects Sugar Labs is evaluating while preserving exact SHA pins. The
activity rows remain provisional migration checkouts and are not treated as
upstream-complete.

The shell remains an ordinary GTK4 top-level on the guest's existing X11
development desktop. Casilda supplies the private Wayland compositor used for
embedded activity surfaces. This is intentional upstream architecture, not a
host display-stack installation.
