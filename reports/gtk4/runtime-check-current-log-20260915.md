# Active GTK4 runtime check — 2026-09-15

After deploying the runner/checker changes and restarting the guest session,
the modern Space check returned:

    runtime-check=ok target=gtk4 pid=14065 desktop=1 window=0x1600005 stable_pid=735 gtk4_pid=14065

The checker now reads the active shell's `ASPARTAME_GTK4_LOG` path and creates
that per-session log before startup. It no longer scans the historical
`gtk4-shell-live.log` for stale fatal markers. The result proves one GTK4 shell
owns the active desktop and private runtime without a stale-log false failure.
