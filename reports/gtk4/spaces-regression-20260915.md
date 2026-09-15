# GTK3/GTK4 Spaces regression check — 2026-09-15

Using the live QEMU guest and the semantic Space controller:

    switch gtk3: exit 0
    runtime-check=ok target=gtk3 pid=735 desktop=0 window=0x400004 stable_pid=735 gtk4_pid=14065
    switch gtk4: exit 0
    runtime-check=ok target=gtk4 pid=14065 desktop=1 window=0x1600005 stable_pid=735 gtk4_pid=14065

The classic GTK3 shell remained healthy while the modern GTK4 shell was
selected, and the modern Space was restored after the comparison. Each check
confirmed the expected active window, workspace, and process identity.
