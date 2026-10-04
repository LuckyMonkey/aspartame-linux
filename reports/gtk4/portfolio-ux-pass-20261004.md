# GTK4 Portfolio UX pass — 2026-10-04

## Result

The packaged GTK4 sweep showed Portfolio's title field but not a usable
project-description workspace. The activity now places the project editor
directly in the expanding root, with a labeled `Project description` frame,
full-height scrolling text surface, visible draft status, and aligned Save
draft/Clear controls.

The UTF-8 Journal title/body payload is unchanged.

## Verification

Focused host check:

```text
pytest -q tests/test_gtk4_portfolio_activity.py
2 passed
```

The rebuilt writable GTK4 guest preview passed:

```text
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
```

Portfolio launched through the real Journal D-Bus path in the headless GTK4
shell. The initial 1920x1080 capture showed the full editor surface; its
SHA-256 was
`f983033d291582e20c7393847011db9f3deb1eb0bc5770456a1f12237112617b`.

A headless QEMU interaction entered `portfolio` in the title field and
activated `Save draft`. The follow-up capture showed `Draft saved: portfolio`;
its SHA-256 was
`fd833d4a8c750cdb29291f8b9bbab810a4fdf0228a0a75bbecd7f6c59d72df42`.

## Boundary

Portfolio remains a `FUNCTIONAL PORT`, not a `FULL PORT`. Rich media and export
features remain open. No GTK3 package was removed.
