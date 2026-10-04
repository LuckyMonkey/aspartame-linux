# GTK4 Diamond Fusion UX pass — 2026-10-04

## Result

Diamond Fusion had a real visual regression in the packaged GTK4 sweep: the
title, status text, and `New game` control were visible, but the puzzle board
surface was blank. The native GTK4 Activity now presents the board as a
responsive, labeled `Puzzle board` frame that expands with the Activity.

The board drawing area keeps a compact minimum size instead of imposing a
fixed calculator-like canvas. The root and board frame expand vertically and
horizontally, while the existing matching/fusion interaction and Journal
payload remain unchanged.

## Verification

Focused host checks:

```text
pytest -q tests/test_gtk4_diamond_fusion_activity.py
1 passed

PYTHONPATH=tests/gtk4_harness python3 tests/gtk4_harness/roundtrip.py packages/gtk4-diamond-fusion-activity
{"package": "gtk4-diamond-fusion-activity", "checks": {"construct": true, "buttons_clicked": 1, "persistent": true, "roundtrip_stable": true, "malformed_tolerated": true}, "errors": []}
```

The rebuilt writable GTK4 guest preview passed:

```text
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
```

The activity launched through the real Journal D-Bus path in the headless
GTK4 shell. The initial 1920x1080 capture showed the complete board surface;
its SHA-256 was
`69e33e23c09e0b52033d63b5c1979f329869e364acf18889cf30a9e36cea9a68`.

Two matching adjacent blue diamonds were then clicked through the headless
QEMU absolute-tablet path, without bringing a VM window to the foreground.
The follow-up 1920x1080 capture showed `Fused! Score: 1` and the merged board
state; its SHA-256 was
`0cb8286ececa2eb7fed0e7f484ac5fd98da89a874aded338c0a29f331e5dff39`.

## Boundary

Diamond Fusion remains a `FUNCTIONAL PORT`, not a `FULL PORT`. The full
cascade/scoring breadth and collaboration behavior remain open. No GTK3
package was removed, and no display history or other state was introduced.
