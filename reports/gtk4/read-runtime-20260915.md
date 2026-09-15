# GTK4 Read runtime boundary — 2026-09-15

The Read implementation now exposes the standard `SimpleActivity` Journal
file hooks. Non-empty UTF-8 payloads are split into form-feed-separated pages;
the sample document remains the empty-object fallback. `write_file` preserves
the pages in the same format.

Because the VM development disk is remounted read-only (`/dev/sda1`,
`errors=remount-ro`), the rebuilt share could not be synchronized. For a
scoped runtime check, the updated module was copied directly into the existing
guest Read bundle and compiled with the guest GTK4 Python 3.14 environment:

    read-module=PASS

The existing Casilda lifecycle probe then completed two real launch/activate/
stop cycles:

    cycle=1 pid=512918 service-ready=PASS shell-active=PASS cleanup=PASS
    cycle=2 pid=513026 service-ready=PASS shell-active=PASS cleanup=PASS
    lifecycle-probe=PASS

This proves module loading and lifecycle coverage only. A Journal object resume
with a user document remains required before Read can move above
`COVERAGE IMPLEMENTATION` in the classification ledger.
