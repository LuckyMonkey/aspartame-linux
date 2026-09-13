# GTK4 semantic Control Panel action — 2026-09-12

After syncing the runtime import path (`/mnt/aspartame-dev/sugar/src`) and
restarting Jarabe, the shell D-Bus action was invoked as the `aspartame` user:

`org.laptop.Shell.ShowControlPanel` → `boolean true`

The action opened the GTK4 Control Panel from Home. The service now tolerates
ShellModel implementations without a private `_main_window` and lets the
ControlPanel establish its own transient relationship.

Screenshot: `reports/screenshots/sugar-20260912-210*.png` (latest capture).
