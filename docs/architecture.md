# Aspartame architecture

Aspartame is an Arch Linux live image built by `archiso`. Sugar is the primary
session and retains its Home, Activity, Frame, Journal, Group, Neighborhood,
palette, and XO-color interaction model. The underlying system remains
conventional Arch: systemd, NetworkManager, pacman, Xorg, Metacity, ordinary
home directories, and a real shell.

The development image uses tty1 autologin and `startx`; it does not use a
display manager. A stable user `.xinitrc` delegates to the system-owned
`aspartame-x-session`, which creates the Sugar D-Bus session and supervises the
shell. `/home/aspartame` is a separate persistent QEMU disk.

Official Arch packages own Sugar, sugar-toolkit-gtk3, sugar-artwork, datastore,
Metacity, and Activities. Aspartame's modified `jarabe` source is isolated under
`sugar-overlay/`, converted reproducibly into the ISO patch, and synchronized
to a generated QEMU development tree. Pacman-owned files are not live-edited.

## Current visual slice

![Activity Manager](screenshots/activity-manager-v0.0.15.png)

![Count Activity](screenshots/count-v0.0.14.png)

These are reference captures of the current Sugar-based vertical slice, not substitutes for runtime tests.

The authoritative runtime/process/import/development map is
[SUGAR-DEVELOPMENT.md](SUGAR-DEVELOPMENT.md). The visual layer map is
[SUGAR-STYLING.md](SUGAR-STYLING.md).
