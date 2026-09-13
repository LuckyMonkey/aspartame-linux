# GTK4 overlay packaging

The standalone image tree now carries the GTK4 Journal overlay at
`/usr/share/aspartame/gtk4-overlay/src/jarabe/journal/listview.py`, alongside
the development-share copy. This removes the previous dependency on the QEMU
9p share for the native Journal implementation.

The development runner still prepends the live overlay for rapid iteration;
GTK3 never imports this path.
