# GTK4 preview bootstrap

This is intentionally separate from stable GTK3 Sugar.

```bash
make sugar-gtk4-init
GTK4_ROOT=/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4 make sugar-gtk4-check
GTK4_ROOT=/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4 make sugar-gtk4-build
```

The initializer checks out exact refs listed in `scripts/sugar-gtk4-init.sh` and records resolved SHAs in the external `PINS.tsv`. The preview venv uses system GTK4 introspection but installs toolkit Python code editable under the preview root. `sugar-ext` installs only under the preview prefix when that build completes.

The launcher is Wayland-first. It requires an existing outer Wayland compositor
and socket, then runs the GTK4 shell with `GDK_BACKEND=wayland`. It does not
silently fall back to X11. Use the explicit diagnostic fallback only when
needed:

```bash
GTK4_BACKEND=x11 make sugar-gtk4-run
```

The current development host is X11 and does not have Weston/Cage installed.
Install Weston through the normal system package workflow, start it nested in
the existing X11 session, and export its `WAYLAND_DISPLAY` before running the
Wayland preview. The shell's inner `wayland-sugar` socket is still created by
Casilda inside Jarabe; the outer compositor is only the GTK display backend.

Preflight without launching:

```bash
GTK4_BACKEND=wayland make sugar-gtk4-check
GTK4_BACKEND=x11 make sugar-gtk4-check
```

A failed Wayland preflight is an honest environment failure, not a GTK4 shell
success claim. Stable GTK3 files and the production session are never touched.
