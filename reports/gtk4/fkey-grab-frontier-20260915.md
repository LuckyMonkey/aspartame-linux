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

## Next step

Verify directly whether the grabs are still held after the release — with
`xev`/`xdotool` or an XQueryKeymap-level probe — rather than trusting the log
line. If they are, the minimum fix is to make the ungrab explicit and
verified instead of relying on object finalisation.

Do not treat this as a Frame defect or a key-routing defect in the GTK4
shell; both were eliminated above.

## Consequence for the deck

W6 and W7 collapse into this one frontier. Semantic Space switching
(`sugar-gtk4-space.sh gtk3|gtk4`) is unaffected and remains the working
comparison mechanism, and all non-function keys — typing, Tab, Shift+Tab,
Enter, Space, Backspace — work in both the shell and embedded Activities.
