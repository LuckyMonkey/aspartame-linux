# F7 does not leave the modern Space — root cause and fix

2026-09-16. Follow-up to the regression recorded in
`reports/gtk4/five-fix-pass-2-20260916.md`.

## Symptom

F8 moved from the classic Space to the modern one. F7 did not move back.
The failure was intermittent across earlier attempts, which is what made it
look like a grab problem.

## What it was not

**Not the key grabber.** The rebuilt `sugar-toolkit-gtk3 0.121-7.1` is
installed and its library carries `XUngrabKey`. The classic shell's overlay
handler releases its passive grabs whenever the modern workspace is
selected — that is deliberate and is exactly what lets the modern Space own
F1-F8 at all:

    WARNING root: Spaces key ownership: GTK3 released (workspace=1)

**Not Metacity.** `jarabe/main.py` runs

    metacity-message disable-keybindings

at startup, so the window manager owns no keys at all. The Spaces
controller writes `org.gnome.desktop.wm.keybindings switch-to-workspace-1 =
['F7', '<Super>Home']`, and Metacity ignores it. Proven two ways: the
key-grab probe never sees Metacity holding F7, and clearing the binding
entirely changes nothing —

    F7 with binding cleared  -> workspace=0
    F7 with binding restored -> workspace=0

Alt+Tab reaching the shell (rather than the window manager) is the same
fact seen from another angle.

**Not the Activity surfaces.** F7 works with Home showing and with an
Activity focused inside the compositor.

## What it was

The modern shell does handle F7/F8 — in `jarabe/main.py`, on a capture-phase
`Gtk.EventControllerKey` attached to `_main_window`, `_overlay` and `stack`:

    space_keys = {Gdk.KEY_F7: "gtk3", Gdk.KEY_F8: "gtk4"}

That binds the Space keys to those widgets alone. They are not in
`_actions_table`, so `KeyHandler.add_window()` — which follows every window
added to the application — does not carry them.

`ControlPanel` is a plain `Gtk.Window` constructed without `application=`,
so it never joins the `Gtk.Application`, `window-added` never fires, and the
shell's key handler never attaches to it.

So **while the Settings control panel is open, no shell key reaches the
keyboard at all.** Measured: with the panel up, F3, F7 and Escape produce no
`GTK4 semantic key event` line — the count of logged key events does not
move.

    A) Home, no activities:          F7 -> 0
    B) Activity surface focused:     F7 -> 0
    C) Settings control panel open:  F7 -> 1     <-- the failure

The earlier intermittency was this: once the control panel had been opened
(with Alt+Shift+M, during the same pass) it could not be dismissed —
Escape, F3 and F4 were dead for the same reason — so every later F7 test
inherited the failing state.

## Fix — patch 0153

One owner for the Space keys, reachable from every window the shell owns:

- `jarabe/view/keyhandler.py`: `'F7': 'space_classic'` and
  `'F8': 'space_modern'` join `_actions_table`, with handlers that spawn the
  Spaces controller and honour `ASPARTAME_SPACE_SWITCHER`, matching the
  classic overlay.
- `jarabe/main.py`: the duplicate capture handling is removed, so there is
  exactly one owner.
- `jarabe/controlpanel/gui.py`: the window registers itself with
  `keyhandler.get_instance().add_window(self)`.

Registering the window is deliberately not the same as adding it to the
application: `ShellModel._window_added_cb` turns a new application window
into a phantom entry in the activity list.

The modal gate is unchanged and still correct. `_non_modal_action_keys` is
`F1`-`F6`, so those stay suppressed while the control panel is modal, while
F7/F8 are not gated and can always leave the Space.

## Proof

A/B on the live guest, control panel open in the modern Space:

    WITHOUT patch: F7 with control panel open -> workspace=1
    WITH patch:    F7 with control panel open -> workspace=0

Regression sweep with the patch applied:

    Home     -> F7 : 0
    classic  -> F8 : 1
    modern   -> F7 : 0
    Activity -> F7 : 0

**Test:** `tests/test_gtk4_space_keys_every_window.py`

## Still open

The Settings control panel cannot be dismissed from the keyboard. Its own
key controller handles Escape, but it is attached in the bubble phase, so
the focused search entry consumes the key first. Separate defect, recorded
not fixed.
