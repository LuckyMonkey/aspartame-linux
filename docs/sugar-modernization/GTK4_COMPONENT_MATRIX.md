# GTK4 component matrix

| Component | Upstream head used | Aspartame state | Arch status | Blocker/action |
|---|---|---|---|---|
| Sugar shell | PR #1106, `f84a2d5` | source checkout only | configure declares GTK4 | build/session smoke required |
| sugar-toolkit-gtk4 | PR #35, `74f6a05` | editable isolated venv | imports; 55 targeted tests pass | upstream enum compatibility fix |
| sugar-ext | main, `563760e` | isolated Meson build | C/tests pass; GIR was blocked | finish typelib build |
| sugar-artwork | main, `3c4854d` | pinned checkout | not installed | shell integration |
| datastore | main, `7aa97e7` | pinned checkout | stable service preserved | GTK4 shell integration |
| Calculate/Log/Browse/ImageViewer/Terminal | pinned migration heads | source only | not installed | test one activity at a time |
