# Keyboard delivery to GTK4 Activities — 2026-09-15

Closes the Sugar → Casilda → Wayland per-keystroke delivery blocker recorded
in `focus-transfer-frontier-20260915.md` and `casilda-keyboard-focus-20260915.md`.

## The chain of four defects

Physical keys reached the shell but never the Activity. Four independent
faults sat in series; each had to go before the next was visible.

1. **The overlay owned window focus.** `_setup_main_window()` made the shell
   `Gtk.Overlay` focusable and set it as the window's focus widget (patch
   0080), on the premise that F1-F8 capture needed it. Capture-phase
   controllers run from the root toward the focus widget, so they only need
   to be *ancestors* of it - the premise was wrong. Meanwhile the overlay is
   an ancestor of the Casilda compositor, so the compositor was never a key
   event's target and its own key controller never ran. Retired by 0140.
2. **Nothing then claimed focus.** With the overlay out of the way the window
   had no focus widget at all (`focus=None`), because nothing on the activity
   stack page grabs it. 0136 grabs it from the stack's own
   `notify::visible-child` and `notify::transition-running` signals - a grab
   issued at switch time does not survive, because a finishing stack
   transition recomputes focus (measured: focus held at t=0 and t=200ms,
   lost by t=1000ms as `transition-running` went False).
3. **The shell swallowed the key.** `KeyHandler._key_pressed_cb` is connected
   to four widgets, so one press arrives once per widget on the path. Its
   duplicate guard returned `True` for every repeat, claiming keys Sugar had
   never acted on and stopping propagation before the compositor. 0139 makes
   it repeat the first dispatch's actual verdict.
4. **Modifiers arrived one keystroke late.** `casilda_compositor_seat_key_notify()`
   read the modifier mask, sent the key, then sent the modifier update. Shift+a
   produced `'a'` and the *following* plain key came through shifted - measured
   as `'aB'` where `'Ab'` was typed. Shift+Tab therefore reached the client as a
   plain Tab and reverse traversal did nothing. 0138 sends modifiers first.

Patch 0137 (keyboard focus for a maximized/fullscreen toplevel at map time)
remains required; without it the seat has no focused surface to deliver to.

## Acceptance evidence

All against the live guest, GTK4 Space, Help Activity launched through
`org.laptop.Journal.LaunchBundle` with **no pointer interaction**.

| # | Criterion | Result |
|---|---|---|
| 1 | Launch a real GTK4 Activity without pointer assistance | PASS — `clean_launch.py`, D-Bus only |
| 2 | Physical typing reaches an editable control | PASS — typed `journal`, `Ab`, `Ok`, `ok` read back from the Help search entry over AT-SPI |
| 3 | Tab / Shift+Tab move through the Activity's real focus chain | PASS — `Search help` → `scroll pane` → `Your XO identity` forward; Shift+Tab returns `scroll pane` → `Search help` |
| 4 | Enter / Space work where semantically appropriate | PASS — Space expanded the focused topic; Enter activated a focused topic button |
| 5 | F7/F8 still switch Spaces | PARTIAL — semantic switching round-trips cleanly (`runtime-check=ok` for gtk3 desktop 0 and gtk4 desktop 1). **Physical** F7/F8 still does not fire; see frontier below |
| 6 | GTK3 remains healthy | PASS — `runtime-check=ok target=gtk3 pid=23078 desktop=0` |
| 7 | Repeated launch → input → stop → relaunch | PASS — three cycles, each typed `ok` into a fresh instance, exactly one Help process alive per cycle, shell healthy after |

Verified once more after all debug instrumentation was removed and Casilda
rebuilt clean: typed `Ok` (correct capitalisation, so modifier ordering holds
in the shipped build), Tab and Shift+Tab both traverse.

## Frontier left explicitly open

**Physical F7/F8 Space switching.** These keys are grabbed by Metacity at the
X11 level, not by Sugar: `switch-to-workspace-1` is `['F7', '<Super>Home']`
and `switch-to-workspace-2` is `['F8']`, both confirmed present on the
session bus Metacity actually uses. A QMP-injected F7 produces no workspace
change and never appears in the shell log, so it is consumed or dropped
before any Sugar code runs. This is the pre-existing environment-sensitive
F-key transport already recorded in the tracker; it is unrelated to the
Sugar → Casilda → Wayland path fixed here, and the focus changes above cannot
affect it, precisely because F7 never reaches the shell process. Semantic
Space switching is unaffected and is the working comparison mechanism.

Not investigated further by deliberate scope limit.
