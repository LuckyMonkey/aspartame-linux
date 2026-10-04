# GTK4 Write UX pass — 2026-10-04

## Result

The packaged GTK4 sweep showed Write with its document editor effectively
missing from the usable Activity workspace. The activity now places a labeled
`Document` frame directly in the expanding root, giving the scrolling text
editor the full available height while keeping draft status and Save draft /
Clear controls visible below it.

The UTF-8 Journal document boundary and save-failure handling are unchanged.

## Verification

Focused host check:

```text
pytest -q tests/test_gtk4_write_activity.py
1 passed
```

The rebuilt writable GTK4 guest preview passed:

```text
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
```

Write launched through the real Journal D-Bus path in the headless GTK4 shell.
The initial 1920x1080 capture showed the full document editor; its SHA-256 was
`cce2a908c0240719931ab41cc020f8595600d131fdbccd5dde52f1aabea23718`.

A headless QEMU interaction entered `draft` and activated Save draft. The
follow-up capture showed `Draft saved (5 characters)`; its SHA-256 was
`4931d99061d65f73da7b7ec5c35c8699290f6d741b21859dcac4777eb7a48179`.

## Boundary

Write remains a `FUNCTIONAL PORT`, not a `FULL PORT`. Rich text and upstream
document-format breadth remain open. No GTK3 package was removed.
