# GTK3 → GTK4 debugging

GTK4 is not a mechanical library rename. Common mechanical ports include
`Gtk.Box.pack_start()` to child APIs, event masks to event controllers,
`Gdk.Screen` to `Gdk.Display`/monitors, old clipboard APIs to `GdkClipboard`,
and `Gtk.Menu` to menu models/popovers. These are good small, reviewable
AI-assisted patches when upstream has an established pattern.

Architecture-sensitive work must be handled separately: Activity lifecycle,
Journal/datastore ownership, Frame activation, clipboard semantics,
drag-and-drop, collaboration, window management, and Wayland compositor
integration. Do not mass-convert those areas.

Capture first failure and environment:

```sh
python3 -c 'import gi; print(gi.__file__)'
python3 -c 'import gi; gi.require_version("Gtk", "4.0"); from gi.repository import Gtk; print(Gtk.get_major_version())'
G_MESSAGES_DEBUG=all GTK_DEBUG=interactive ./scripts/sugar-gtk4-smoke.sh
make sugar-logs
```

Classify each failure as upstream, Arch dependency drift, Aspartame
integration, X11/Wayland backend, or activity-specific. Never hide a
traceback by weakening the smoke test.
