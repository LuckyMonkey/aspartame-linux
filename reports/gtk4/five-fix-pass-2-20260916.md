# Five-defect pass 2 — 2026-09-16

Second bounded find-and-fix pass. Five independent defects, each found by
using the system, each reproduced before it was changed and proven after.
Discovery stopped at five.

Environment: guest VM, classic GTK3 Space on workspace 0 and modern GTK4
preview Space on workspace 1.

---

## 1 — Calculate's keypad inserted nothing

**Commit:** `fcdbfa6`

**Reproduction:** launch Calculate, click 7, +, 8, = with the pointer. The
entry stays on its placeholder and the result reads "Invalid expression".
Typing the same characters on the keyboard gives 15, so the evaluator and
the `=`/`Clear` buttons were fine.

**Root cause:** `_button_clicked` called
`self.entry.insert_text(label, len(label), position)`. GTK4's
`Gtk.Editable.insert_text` takes `(text, position)`. Run directly against
the preview's GTK4:

    TypeError: Editable.insert_text() takes 3 positional arguments but 4 were given

GTK swallows exceptions raised inside a `clicked` handler, so every press
silently did nothing.

**Fix:** drop the spurious length argument.

**Proof:** clicking 7, +, 8, = shows `7+8` then `15`, entirely by pointer.

**Test:** `tests/test_gtk4_calculate_keypad.py`

---

## 2 — The Share palette claimed a share that never happened

**Commit:** `5434730` — `patches/gtk4-preview/0149-...`

**Reproduction:** open any Activity's Share palette and choose "My
Neighborhood". Nothing is shared, nothing is said, and the radio stays
selected on "My Neighborhood" for the rest of the session.

**Root cause:** `Activity.share()` raises `NotImplementedError` in the GTK4
port, and `ShareButton.__neighborhood_clicked_cb` called it straight from
the palette item's `clicked` handler. All 50 preview Activities carry the
button and it is sensitive in every one (`max_participants = 0`).

A first fix that reverted the radio inside the handler did not hold:
`RadioPalette._on_button_clicked` is connected after `ShareButton`'s own
handler and re-activates whatever was clicked. Runtime probe:

    neighborhood sensitive = True active(before) = False
    raised: [NotImplementedError('Activity sharing not yet implemented...')]
    active(after) = True private.active = False

**Fix:** catch the refusal, defer the undo to `GLib.idle_add` so it outlives
the emission, and undo it by clicking "Private" — the same path the user
takes, so the menu button's icon and label follow the radio back. Raise the
toolkit's own `NotifyAlert` so the refusal is visible. Sharing is still not
implemented; the toolbar just stops lying about it.

**Proof:**

    WARNING:root:Activity sharing is unavailable: Activity sharing not yet implemented...
    active(after) = False private.active = True
    alerts shown: [('Sharing is unavailable', 'This activity could not be shared with your neighborhood.')]

**Test:** `tests/test_gtk4_share_button_revert.py`

---

## 3 — Sugar tool button accelerators were never installed

**Commit:** `1a2e39c` — `patches/gtk4-preview/0150-...`

**Reproduction:** launch Write in the modern Space and press Ctrl+Q. The
Activity keeps running. The same is true of every accelerator the toolkit
sets on a plain tool button: Stop's Ctrl+Q, Undo's Ctrl+Z, Redo's Ctrl+Y,
Copy's Ctrl+C, Paste's Ctrl+V.

**Root cause:** `activityinstance.main()` constructs the Activity — toolbar
and all — and only then calls `app.add_window(activity)`. A `ToolButton`'s
`notify::root` therefore fires while `root.get_application()` is still
`None`, `_add_accelerator()` returns early, and nothing retries. Reproducing
the real launch path showed:

    activity application: <Gtk.Application ...>
    tool buttons with an accelerator: 'Stop' -> <Ctrl>Q
    app actions: []
    actions bound to <Ctrl>Q: []

`ToggleToolButton` already has the missing half — it connects `map` and
re-runs `_add_accelerator` there, by which time `add_window()` has happened.
`ToolButton` was never given the same retry.

**Fix:** give `ToolButton` the same map retry, and remember the installed
action so a repeated map replaces it instead of leaking another one.

**Proof, A/B on the live guest with Write:**

    WITH patch, before: 1   after ctrl+q: 0
    WITHOUT patch, before: 1   after ctrl+q: 1
    WITH patch, before: 1   after ctrl+q: 0

**Test:** `tests/test_gtk4_toolbutton_accelerator.py`

---

## 4 — Alt+Tab raised on every press

**Commit:** `ef52b01` — `patches/gtk4-preview/0151-...`

**Reproduction:** run two Activities in the modern Space and press Alt+Tab.
Nothing switches and the shell log carries:

    File "jarabe/model/shell.py", line 581, in get_next_activity
      i = activities.index(current)
    ValueError: list.index(x): x not in list

**Root cause:** `get_next_activity()`/`get_previous_activity()` index
`_get_activities_with_window()`, which keeps only entries that registered a
Gtk window with the shell. That held in GTK3, where each Activity had an X
window the shell saw. In the modern Space an Activity is a Wayland client
inside the Casilda compositor and never registers one. Instrumenting the
live shell with Clock and Stopwatch running:

    all=[None, 'tv.alterna.Clock', 'org.sugarlabs.StopwatchActivity']
    with_window=[None]
    active='org.sugarlabs.StopwatchActivity'

Every Activity is tracked, none is window-backed, and the active one is
never in the list being indexed. The `len(activities) == 0` guard sat
*after* the `index()` call, so it could never run either.

**Fix:** walk the activities the shell tracks through their D-Bus service —
the same set the Frame shows — skipping the shell's own entry, which has no
bundle id. Guard the index before using it.

**Proof:** instrumented `activate_activity` on the live shell:

    activate_activity('tv.alterna.Clock') active_was='org.sugarlabs.StopwatchActivity'
    activate_activity('org.sugarlabs.StopwatchActivity') active_was='tv.alterna.Clock'

No exception; the selection alternates correctly.

**Limitation, recorded not fixed:** the selected Activity's surface is not
raised on screen. The shell has one compositor page for all Activities and
Casilda exposes `casilda_compositor_focus_toplevel` but no way to enumerate
or raise a chosen toplevel. That is compositor work, not a bounded fix.

**Test:** `tests/test_gtk4_shell_alt_tab.py`

---

## 5 — Every Alt+Shift global key was dead

**Commit:** `02fc7b6` — `patches/gtk4-preview/0152-...`

**Reproduction:** press Alt+Shift+M on Home. The Settings control panel does
not open. Same for Alt+Shift+F (Frame), Alt+Shift+O (search), Alt+Shift+Q
(logout) and Alt+Shift+D (dump UI tree).

**Root cause:** holding Shift makes the keyval the capital letter, so
`Gdk.keyval_name()` returns `'M'`. The branch that builds the
`'<alt><shift>'` prefix tested membership in `['f', 'm', 'o', 'q', 'd']`, so
it never fired, the key stayed `'M'`, and `_actions_table` — keyed
`'<alt><shift>m'` — never matched. The shell log showed the key arriving and
nothing happening:

    WARNING:root:GTK4 semantic key event: Alt_L
    WARNING:root:GTK4 semantic key event: Shift_L
    WARNING:root:GTK4 semantic key event: M

**Fix:** test the lowercase form and build the key from it.

**Proof:** before, Alt+Shift+M left Home unchanged
(`sugar-20260916-023944-v0.0.31.png`); after, it opens the Settings control
panel (`sugar-20260916-024137-v0.0.31.png`).

**Test:** `tests/test_gtk4_keyhandler_alt_shift.py`

---

## Checked and found correct — no defect

- **Multiple Activities coexisting.** An earlier sweep suggested launching an
  Activity terminated the previous one. It did not: the sweep used wrong
  bundle ids and those launches simply failed
  (`Activity with the bundle_id org.sugarlabs.Portfolio was not found`).
  Clock and Stopwatch run together; Write stays alive past 25 seconds.
- **ImageViewer's zoom and rotate buttons.** They raise with no image
  loaded, but `list_set_sensitive(self._image_buttons, False)` leaves them
  insensitive until one loads, so a user cannot reach them. Confirmed at
  runtime: `zoom-in sensitive=False effective=False`.
- **ImageViewer's `os.link` into the instance directory.** Cross-device only
  under a synthetic `SUGAR_ACTIVITY_ROOT`; the real root is on the same
  filesystem as the datastore.

## Open findings — reproduced, left open

- **Settings → Language crashes on construction.** The image ships three
  locales (`C`, `C.utf8`, `POSIX`), so `read_all_languages()` returns
  nothing and `_language_dict`/`_country_dict` are empty. `_add_row()` falls
  back to `'English'` and `_build_country_list` raises
  `KeyError: 'English'`. Reproduced in an isolated process. The section
  should degrade rather than raise. Found at defect six, so not pursued.
- **The Settings control panel cannot be dismissed from the keyboard.**
  Escape, F3 and F4 all leave it up and every keystroke goes to its search
  entry. Related to the recorded finding that the Settings window does not
  cover the screen.
- **The shell logs every keystroke at WARNING.**
  `keyhandler._dispatch_key` calls
  `logging.warning("GTK4 semantic key event: %s", key)` on every press, so
  typed text lands in the shell log and real warnings are buried.

## Regression observed while closing the pass

**F7 no longer returns from the modern Space to the classic one.** F8
(classic → modern) works; F7 (modern → classic) does nothing, repeatedly.
EWMH switching works (`sugar-x11-workspace.py switch 0` moves to workspace
0), so the Spaces themselves are healthy. The key-grab probe shows the
asymmetry:

    on workspace 1 (modern):  grabbed-elsewhere=none
    on workspace 0 (classic): grabbed-elsewhere=F1,F2,F3,F4,F5,F6,F7,F8

so nothing holds F1-F8 while the modern Space is current. The rebuilt
`sugar-toolkit-gtk3 0.121-7.1` is installed and its library contains
`XUngrabKey`, and re-running `sugar-gtk4-space.sh setup` with the user's
runtime dir and Metacity's session bus did not restore F7.

None of the five fixes touch F-key routing: 0152 only rewrites Alt+Shift
letter chords, 0151 only the shell model's activity list, 0150 and 0149 the
toolkit's tool buttons. This appeared after a full graphical-session restart
performed during this pass and needs re-verification from a clean boot
before W6/W7 can be called green again.
