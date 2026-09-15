# GTK4-024 — Tab never crosses from the shell into the embedded Activity surface — 2026-09-15

`qemu-function-keys-20260915.md` recorded that a physical Tab + Space on a
live Activity "produced no visible control-state change" and left
Tab/Shift+Tab/Space explicitly unverified. With the AT-SPI bus-discovery fix
in `atspi-bus-discovery-20260915.md` (GTK4-023) it is now possible to check
*where keyboard focus actually is*, independent of rendering.

## Reproduction

With the modern Space active and the native Help Activity running
(pid 15138 = Jarabe shell, pid 25376 = Help Activity, a separate process):

1. Baseline probe (`scripts/sugar-gtk4-focus-probe.py`, before any key):

       focused=1 pid=15138 role=panel name='' path=Sugar < python

2. After one physical Tab (`scripts/qemu-send-key.py TAB`):

       focused=1 pid=15138 role=panel name='' path=panel < grouping < panel < Sugar < python

3. A second and third Tab produce the identical line — focus does not move
   again.

4. Dumping the Help Activity's own AT-SPI tree (pid 25376) at the same
   moment shows a complete, correctly labeled, *focusable* widget tree
   (the "Search help" entry, the scroll pane, and one button per topic,
   e.g. `button 'Keyboard and accessibility' focusable=True`) — but every
   single node reports `focused=False`, including the Activity's own
   top-level `application` and `frame` nodes.

## Diagnosis

Tab is not being swallowed by Sugar's semantic key handler:
`KeyHandler._key_pressed_cb` (`src/jarabe/view/keyhandler.py`) only treats
`<alt>Tab`/`<alt><shift>Tab` specially and returns `False` for a bare Tab,
so GTK's normal focus-chain traversal is left to run. That traversal moves
focus once, from the Jarabe window itself down into the `Gtk.Stack`'s
"activity" child (patch `0070-main-compositor-key-capture.patch` attaches a
capture-phase controller to exactly that widget,
`shell_instance.compositor`), and then stops: `compositor` is GTK4's only
representation of Casilda's embedded Wayland surface, and GTK's focus chain
has no visibility into whatever is drawn inside it.

The embedded Activity's own top-level frame never reports
`STATE_FOCUSED`, which means keyboard focus was never handed to that
Wayland client at the compositor/seat level in the first place. Reaching
individual Activity widgets (the Help search entry, an expander button) by
Tab requires Casilda to forward keyboard focus into the embedded surface
(a `wl_keyboard` enter/seat-focus operation) when its GTK widget becomes the
focused child of the shell stack — a separate step from GTK4's own
widget-level focus chain, which stops at the compositor widget's boundary
by design.

This sharpens, rather than repeats, the existing gate item: physical
transport (QMP → evdev → GTK) is proven (`qemu-function-keys-20260915.md`);
GTK's own shell-level focus chain is proven to move on Tab; the missing
piece is specifically compositor-to-client keyboard-focus handoff, which is
Casilda-owned, not a shell or Activity defect. Do not mark Tab/Shift+Tab/
Space as verified until an embedded Activity widget itself reports
`STATE_FOCUSED` after a physical Tab.

## Not attempted here

Wiring Casilda's keyboard-focus handoff is compositor/Wayland-protocol work,
not a shell-side Python change, and is out of scope for this pass per the
project's own rule to keep architecture-sensitive work (compositor
integration, focus semantics) separate from small reviewable patches. The
next step is to inspect Casilda's own GTK4 widget API (pinned separately;
see `PINS.tsv`) for a seat/keyboard-focus method to call when
`shell_instance.compositor` becomes the visible stack child.
