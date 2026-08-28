# Python-first policy

The Arch system interpreter remains pacman-owned. Aspartame must never use
`sudo pip install` against `/usr/bin/python`.

Future user/application environments belong under a user-owned namespace such
as `~/.aspartame/envs/` and `~/.aspartame/activities/`. Python Activities should
be inspectable and cloneable without making system-critical files editable in
place.

Python should orchestrate NetworkManager, BlueZ, CUPS, PipeWire, UPower,
udisks, and systemd through supported interfaces rather than replacing those
services.

