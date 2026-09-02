# GTK4 preview bootstrap

This path runs **inside the Aspartame development VM only**. The entry scripts
reject execution outside an image with `IMAGE_ID=aspartame`. They do not
install or configure a host Wayland session.

The ISO profile supplies current Arch GTK4, PyGObject, Wayland, wlroots 0.20,
Meson, GI, and build tools. Casilda itself is the embedded compositor, so
Weston is neither installed nor part of the runtime architecture.

The repository is exposed to the guest through the existing 9p development
share. Stage the scripts and preview patches there after changing them:

```bash
cp -a scripts /media/freezer/SteamLibrary/vms/aspartame-build/runtime/aspartame-dev/gtk4-preview/
cp -a patches/gtk4-preview /media/freezer/SteamLibrary/vms/aspartame-build/runtime/aspartame-dev/gtk4-preview/patches/
```

Then, inside the VM as `aspartame`:

```bash
export GTK4_ROOT=/home/aspartame/Development/gtk4-preview
/mnt/aspartame-dev/gtk4-preview/scripts/sugar-gtk4-init.sh
/mnt/aspartame-dev/gtk4-preview/scripts/sugar-gtk4-build.sh
DISPLAY=:0 XAUTHORITY=/home/aspartame/.Xauthority \
    /mnt/aspartame-dev/gtk4-preview/scripts/sugar-gtk4-run.sh
```

The initializer records every requested ref and resolved SHA in
`$GTK4_ROOT/PINS.tsv`. Build products go under `$GTK4_ROOT/prefix`; mutable
profile, schema, and compositor state goes under `$GTK4_ROOT/runtime`. Neither
path overlaps `/usr`, package-owned `sugar3`, or stable Sugar's profile.

The launcher creates a private D-Bus session and exports the isolated Python,
GI typelib, library, schema, and Sugar data paths. Jarabe creates a normal
GTK4 preview window on the current guest display. Its embedded Casilda widget
owns `$GTK4_ROOT/runtime/wayland-sugar` for Wayland activity clients.

Verify the compositor from another guest shell:

```bash
XDG_RUNTIME_DIR="$GTK4_ROOT/runtime" \
WAYLAND_DISPLAY=wayland-sugar \
wayland-info
```

FIRST PIXELS is verified. This command does not yet produce a usable desktop:
the next runtime blocker is the datastore D-Bus service-name mismatch, followed
by locale propagation into the private session. See `BLOCKERS.md`.
