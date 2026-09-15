# Active GTK4 session log capture — 2026-09-15

After deploying the runner with tee-backed per-session logging, the live guest
reported:

    pid=14725
    log=/home/aspartame/Development/gtk4-preview/logs/gtk4-shell-20260915T150529Z.log
    runtime-check=ok target=gtk4 pid=14725 desktop=1 window=0x1600005

The log contains current dbus, Telepathy, VFS, and shell startup output. This
confirms runtime diagnostics are tied to the active modern Space rather than a
stale historical file.
