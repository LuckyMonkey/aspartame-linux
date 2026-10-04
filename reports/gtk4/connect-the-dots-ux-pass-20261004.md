# GTK4 Connect the Dots UX pass — 2026-10-04

## Result

The packaged GTK4 sweep showed Connect the Dots with only its title, status,
and `New puzzle` button; the numbered puzzle canvas was effectively lost in
the nested layout. The activity now puts a labeled `Dot canvas` directly in
the expanding root, with the aspect-preserving puzzle surface filling the
available Activity workspace.

The numbered-dot drawing and Journal progress model are unchanged. The canvas
also has a visible Sugar-style surface boundary and retains the existing
pointer hit targets.

## Verification

Focused host check:

```text
pytest -q tests/test_gtk4_connectthedots_activity.py
1 passed
```

The rebuilt writable GTK4 guest preview passed:

```text
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
```

Connect the Dots launched through the real Journal D-Bus path in the headless
GTK4 shell. The initial 1920x1080 capture showed the labeled canvas and all
eight numbered points; its SHA-256 was
`0c702712783993f45d2e9f08e69d9ea18d0a5ea70dd963f1b1f7797865f0d120`.

A headless QEMU pointer click on point 1 changed the status to `Connect dot 2`
and highlighted point 1. The follow-up 1920x1080 capture checksum was
`b82a4aa781e70738a378588807ffa889c3f154b819320068cd222e69328fc383`.

## Boundary

Connect the Dots remains a `FUNCTIONAL PORT`, not a `FULL PORT`. Full artwork
and collaboration behavior remain open. No GTK3 package was removed.
