# GTK4 focus-ring and build frontier — 2026-09-15

The guest preview build was rerun after semantic patch handling was added for
the current Journal and Neighborhood sources. It advanced through patch 0135
and completed Casilda, sugar-ext, Jarabe, datastore, and toolkit staging:

    GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS

The old VTE/WebKit dependency checks were removed because the modern Terminal,
Browse, and Help activities use native GTK4 surfaces and do not import those
GTK3-era runtimes.

After restarting the modern shell from the rebuilt guest prefix, Count was
launched through the Journal D-Bus service and accepted a physical QEMU Tab
event. The resulting 1920x1080 capture is:

    reports/screenshots/sugar-20260915-103741-v0.0.31.png
    SHA-256: 5bbdbc3c35fa608ff11c367a4a5e9fea1eb74a20c04b3c1e8759021ae5cf1dc2

The capture shows the live Count Activity surface, Sugar activity chrome, and
the blue focus indication on the activity icon. This proves the rebuilt focus
style is installed and the Activity surface is visible. It does not claim the
full Tab/Shift+Tab/Space completion gate; deterministic action results remain
tracked separately in `CONVERSION_TRACKER.md`.
