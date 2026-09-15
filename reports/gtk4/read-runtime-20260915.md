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

This initial check proved module loading and lifecycle coverage only. The later
`read-roundtrip-20260915.md` probe added live seeded UTF-8 Journal object
resume evidence, promoting Read to a bounded `FUNCTIONAL PORT` while leaving
PDF/EPUB and full upstream format parity unclaimed.
