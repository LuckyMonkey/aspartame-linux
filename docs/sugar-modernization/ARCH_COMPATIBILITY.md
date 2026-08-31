# Arch compatibility

Aspartame currently relies on Arch package names and a Python 3.14 runtime,
with Sugar 0.121-7 pinned for the live overlay. Rolling changes can affect
PyGObject, GTK, GLib, WebKitGTK, D-Bus bindings, NetworkManager, Xorg,
Metacity, and Python packaging independently.

Check before changing packages:

```sh
make sugar-info
pacman -Q sugar sugar-toolkit-gtk3 sugar-artwork sugar-datastore python
pacman -Qi sugar sugar-toolkit-gtk3
```

Never use `sudo pip` against system Python. Verify package ownership with
`pacman -Qo`, keep package pins and hashes in the repository, and treat an
Arch upgrade as a compatibility event requiring the stable smoke test.
