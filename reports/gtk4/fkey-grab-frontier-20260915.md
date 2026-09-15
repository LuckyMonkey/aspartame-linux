# F-key delivery to the modern Space — frontier — 2026-09-15

W7 (Frame navigation) and W6 (F7/F8 Space switching) are the same defect:
**no function key reaches the GTK4 shell while the classic GTK3 shell is
running**, even though ordinary keys do.

## What was measured

Instrumentation was added temporarily at the shell's own first capture point
(`_capture_zoom_key` in `jarabe/main.py`, a CAPTURE-phase controller on the
window, the overlay and the stack) and then removed:

- Typing `a` logged three times — once per capture controller on the path.
- F1, F3, F5 and F6 produced **no log line at all**, and no view change.

So the keys are not being consumed by Sugar's own handlers or by focus
routing. They never arrive.

Ruled out along the way:

- **Not the Frame.** `Frame.toggle()` never runs on F6 (instrumented and
  confirmed silent), and the top-left hot corner — which reaches the same
  `toggle()` — also fails to reveal the Frame from a verified Home view.
- **Not this session's focus work.** Reverting 0140, restarting and
  retesting still produced nothing.
- **Not a stuck modifier.** Every modifier was explicitly released over QMP;
  F1 still did nothing.
- **Not Metacity, except for F7/F8.** Its only F-key bindings are
  `switch-to-workspace-1 = ['F7', '<Super>Home']` and
  `switch-to-workspace-2 = ['F8']`.
- **Not the GTK3 control panel being open.** Closing it changed nothing.

## The remaining suspect

The classic GTK3 shell owns Sugar's shell keys through
`SugarExt.KeyGrabber`, which installs **global X11 passive grabs**. The
dual-Space design already knows about this: `_sync_space_grab()` in the
packaged GTK3 `keyhandler.py` is supposed to release those grabs whenever the
modern Space is selected, and its own log says it does:

    Spaces key ownership: GTK3 released (workspace=1)

with the workspace confirmed as 1 at the same moment. Yet F-keys still do not
reach the modern shell. The release path is

    grabber.grab_keys([])
    del grabber

and its own comment notes that on some versions `grab_keys([])` only updates
the requested key list, so dropping the object is relied on as the real
ungrab. A Python `del` of a local name does not guarantee GObject
finalisation, so the X11 passive grabs may well outlive the "released" log
line.

## The classic shell cannot simply be stopped

Stopping the GTK3 shell to test the hypothesis does not work: it is
supervised and respawned within seconds, and the respawned instance lands on
whichever workspace is current, covering the modern Space until
`sugar-gtk4-space.sh setup` reconciles placement. So "run only one shell" is
not an available workaround, and the fix has to be a correct ungrab rather
than avoiding the contention.

## Direct observation: the grabs are never released

`scripts/sugar-x11-keygrab-probe.py` answers this without guessing. X11 allows
only one client to hold a passive grab on a key, so asking for the grab and
catching `BadAccess` says whether someone else owns it. Run with the modern
Space selected, while the classic shell logged
`Spaces key ownership: GTK3 released (workspace=1)`:

    F1     keycode=67  HELD by another client
    F2     keycode=68  HELD by another client
    F3     keycode=69  HELD by another client
    F4     keycode=70  HELD by another client
    F5     keycode=71  HELD by another client
    F6     keycode=72  HELD by another client
    F7     keycode=73  HELD by another client
    F8     keycode=74  HELD by another client
    Tab    keycode=23  free
    a      keycode=38  free

Exactly the observed symptom: ordinary keys reach the modern shell, function
keys never do.

The owner is the classic shell. Killing it and probing inside the respawn
window, before it re-grabs, reports every one of F1-F8 as `free`.

Three release strategies were tried in the classic shell's
`_sync_space_grab`, with the probe re-run after each, and **none** dropped the
grabs:

1. `grabber.grab_keys([])` as shipped - still held.
2. Adding `grabber.run_dispose()` to force GObject disposal - still held.
3. Replacing the set with a single unused key,
   `grab_keys(['XF86LaunchA'])` - still held.

So `SugarExt.KeyGrabber`'s grabs are additive and are released only when the
owning process exits. The classic shell's release path cannot work as
written, whatever its log line says. All three experiments were reverted and
the classic shell is back to its original source; both Spaces were verified
healthy afterwards.

## Where the fix belongs

In `SugarExt.KeyGrabber` itself: `grab_keys()` has to `XUngrabKey` the keys it
previously took before applying a new set, so that an empty set is a real
ungrab. The implementation ships in **`sugar-toolkit-gtk3 0.121-7`**
(`/usr/lib/libsugarext.so`, `SugarExt-1.0.typelib`), so closing this means
rebuilding that package with a corrected key grabber, and it is an upstream
candidate. Its source is not checked out on this guest; only the GTK4
`sugar-ext` is pinned here, and that one does not contain the key grabber.

The alternative, calling `XUngrabKey` directly from the classic shell, needs
the shell's *own* X connection, because passive grabs are per-client: a fresh
`XOpenDisplay` is a different client and cannot release them. PyGObject
exposes the GTK3 `Display*` only through the repr of a boxed `xlib.Display`,
so doing this from Python means parsing a pointer out of a string. That is
not worth shipping into the classic shell's key handling.

Do not treat this as a Frame defect or a key-routing defect in the GTK4
shell; both were eliminated above.

## Consequence for the deck

W6 and W7 collapse into this one frontier. Semantic Space switching
(`sugar-gtk4-space.sh gtk3|gtk4`) is unaffected and remains the working
comparison mechanism, and all non-function keys — typing, Tab, Shift+Tab,
Enter, Space, Backspace — work in both the shell and embedded Activities.
