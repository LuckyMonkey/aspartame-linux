# GTK4 activity UX pass — Log pane

Date: 2026-10-04
Environment: headless QEMU, 1920×1080, GTK4 preview, no host mouse grab

The GTK4 Log activity now gives its `Gtk.Paned` a stable 420px file-list
viewport and keeps the detail text view available for the remaining width.
This corrects the previous layout where the list consumed nearly the entire
surface and the detail pane was squeezed to the far edge.

The change is a pinned build patch,
[`0171-log-activity-pane-layout.patch`](../../patches/gtk4-preview/0171-log-activity-pane-layout.patch),
applied after the existing GTK4 ListBox port. The packaged runtime bundle was
also overlaid with the patched source for verification.

Evidence:

- targeted Log visual capture: 1920×1080 PASS;
- full headless sweep: `pass=50 fail=0`;
- GTK4 runtime check: `runtime-check=ok`;
- Log launches and stops cleanly through the visual sweep.

The detail pane visibly contains historical datastore shutdown/log text. That
is the Log activity displaying log content, not evidence of a current Log
Activity crash; the runtime checker found no fatal marker in the active GTK4
session log. The datastore shutdown traceback remains an environment-noise
follow-up for the QEMU session and is not hidden by this UI change.
