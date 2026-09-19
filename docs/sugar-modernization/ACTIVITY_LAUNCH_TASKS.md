# GTK4 Activity launch task ledger

**Status:** launch coverage is proven; parity work is explicitly queued per Activity.

The 2026-09-19 live one-cycle matrix proved all 50 bundles below can be
resolved, started through the GTK4 launcher/Casilda boundary, activated, and
stopped without leaving an orphan process. That is **runtime coverage**, not a claim
that the Activity is a complete port. The authoritative port class remains in
[`ACTIVITY_PORT_CLASSIFICATION.md`](ACTIVITY_PORT_CLASSIFICATION.md).

This ledger is the hand-off list for the next pass. It deliberately does **not**
try to make every Activity look identical. Sugar Activities are allowed to keep
their own visual language; the shell should provide a consistent frame and
semantic lifecycle, while Activity-specific artwork and layout remain a later,
bounded task.

## Task vocabulary

Each row names the next checks for that Activity. Tasks are ordered by value,
not by the order in which the matrix launches bundles.

- **ICON** — verify bundle metadata, icon loading, XOColor normalization, and
  stopped/launching/running/active state rendering.
- **CHROME** — inspect Activity top-bar/toolbar ownership and launch debris;
  this means documenting the mismatch and fixing the shell boundary, not
  flattening the Activity into one visual style.
- **INPUT** — prove pointer and keyboard actions reach the Activity and map to
  Sugar semantic actions.
- **STATE** — prove Home/Frame state follows authoritative lifecycle state and
  clears on stop or abnormal exit.
- **PERSIST** — verify Journal save, resume, metadata, and failure/retry paths.
- **A11Y** — expose names, roles, focus order, and Escape/Enter/Space behavior.
- **PEER** — compare the supported collaboration/share behavior where the
  Activity actually advertises it.
- **PORT** — compare remaining workflow breadth with the GTK3/reference
  Activity; no visual rewrite is implied.

## Per-Activity launch lists

All rows below have `LAUNCH=PASS` from the 2026-09-19 matrix. A row is complete
only when its listed follow-up tasks have independent evidence; matrix PASS is
never promoted to FULL PORT by itself.

| Activity (bundle ID) | Launch result | Next task list |
| --- | --- | --- |
| Help (`org.laptop.HelpActivity`) | PASS | ICON, CHROME, INPUT, STATE, A11Y, PORT — retain child-readable help and finish shell-wide chrome boundary. |
| Count (`org.aspartame.Count`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — keep the current voxel workflow; separately document layer/grid editing gaps. |
| Calculate (`org.aspartame.Calculate`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — exercise editor focus, expression errors, and Journal resume. |
| Clock (`tv.alterna.Clock`) | PASS | ICON, CHROME, STATE, A11Y, PORT — verify time refresh, stop cleanup, and reference presentation. |
| JAMClock (`org.laptop.JAMClock`) | PASS | ICON, CHROME, STATE, A11Y, PORT — verify clock identity/icon mapping and shell state transitions. |
| Image Viewer (`org.laptop.ImageViewerActivity`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — verify selection, zoom/navigation, and object resume. |
| Terminal (`org.laptop.Terminal`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — retain the functional command surface while checking terminal focus and object recovery. |
| Browse (`org.laptop.WebActivity`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — document the offline boundary; do not imply WebKit/download parity. |
| Log (`org.laptop.Log`) | PASS | ICON, CHROME, INPUT, STATE, A11Y, PORT — verify filtering, scrolling, and readable focus behavior. |
| Mastermind (`org.laptop.Mastermind`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare scoring, hints, and reset semantics. |
| Poll (`org.worldwideworkshop.PollBuilder`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PEER, PORT — preserve editor/vote separation and document collaboration scope. |
| Mancala (`mulawa.Mancala`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PEER, PORT — compare rules, stores, turn state, and sharing. |
| Reversi (`net.coderanger.olpc.reversi`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PEER, PORT — compare legal moves, scoring, hints, and sharing. |
| Jumble (`mulawa.Jumble`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare puzzle breadth, hints, and score persistence. |
| NumberRush (`org.sugarlabs.NumRush`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PEER, PORT — compare progression, difficulty, scoring, and sharing. |
| Across and Down (`mulawa.AcrossDown`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare full grid/clue editing and recovery. |
| IQ (`mulawa.IQ`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare puzzle catalog and progression. |
| Appel Haken (`mulawa.AppelHaken`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare map breadth, validation, and reset behavior. |
| BallAndBrick (`org.sugarlabs.BallAndBrick`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare physics, timing, and restart semantics. |
| Implode (`com.jotaro.ImplodeActivity`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare cascade/scoring and board recovery. |
| PlayGo (`org.laptop.PlayGo`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PEER, PORT — compare captures, scoring, and sharing. |
| BlockParty (`org.laptop.BlockPartyActivity`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare rotation, puzzle breadth, and recovery. |
| Typing Turtle (`org.laptop.community.TypingTurtle`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare exercise progression, scoring, and audio boundaries. |
| Memorize (`org.laptop.Memorize`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PEER, PORT — compare randomization, scoring, and collaboration. |
| Maze (`vu.lux.olpc.Maze`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare generation, navigation, and restart behavior. |
| FotoToon (`org.eq.FotoToon`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare image import, layout, captions, and export. |
| Portfolio (`org.sugarlabs.PortfolioActivity`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare rich media, project navigation, and export. |
| Markdown (`org.sugarlabs.Markdown`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare parser/rendering breadth and object recovery. |
| Finance (`org.laptop.community.Finance`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare charts, import/export, and accounting workflows. |
| Words (`org.laptop.Words`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare dictionary, translation, and audio boundaries. |
| LOL (`org.olpc-france.LOLActivity`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — identify the reference workflow before expanding coverage. |
| Get Things Done (`org.sugarlabs.GTDActivity`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare task ordering, filtering, and recovery. |
| Grid Paint (`org.olpcfrance.Gridpaint`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare drag-fill, layers, and export semantics. |
| Stopwatch (`org.sugarlabs.StopwatchActivity`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare laps, timing accuracy, and resume. |
| Gears (`org.sugarlabs.GearsActivity`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare animation controls and object recovery. |
| TurtleBlocks (`org.laptop.TurtleArtActivity`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare block language, drawing, and project recovery. |
| Game Of Life (`org.sugarlabs.gameOfLife`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare pattern editing, stepping, and generation persistence. |
| Color My World (`org.sugarlabs.ColorMyWorldActivity`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare artwork tools, palette semantics, and object recovery. |
| Abacus (`com.homegrownapps.abacus`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare bead manipulation and place-value workflows. |
| Planets (`org.sugarlabs.Planets`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare simulation controls and object recovery. |
| Write (`org.sugarlabs.Write`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — preserve text save/resume while tracking rich document gaps. |
| Connect the Dots (`org.sugarlabs.ConnectTheDots`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare full artwork, undo, and completion semantics. |
| Pippy (`org.laptop.Pippy`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare editor/runtime breadth, errors, and project recovery. |
| Paint (`org.sugarlabs.Paint`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare layers, tools, undo, and image object recovery. |
| Diamond Fusion (`com.francocorrea.diamondfusion`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare cascade/scoring and board recovery. |
| Level (`net.flossmanuals.LevelActivity`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare calibration and hardware-sensor boundary. |
| Moon (`com.garycmartin.Moon`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare phase model and astronomy breadth. |
| Get Books (`org.laptop.sugar.GetBooksActivity`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — preserve offline catalog behavior and document network/download scope. |
| Jukebox (`org.laptop.sugar.Jukebox`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — compare playlist, codec, and media playback boundaries. |
| Read (`org.laptop.sugar.ReadActivity`) | PASS | ICON, CHROME, INPUT, STATE, PERSIST, A11Y, PORT — preserve UTF-8 resume while tracking PDF/EPUB breadth. |

## Shell-wide queue (do once, not once per Activity)

These are intentionally centralized so every Activity does not grow a bespoke
fix for the same shell problem:

1. **SHELL-ICON:** trace bundle metadata → XOColor → GTK texture during launch;
   capture one failing and one successful Activity and fix the shared owner.
2. **SHELL-CHROME:** inspect the launch screenshot's top-bar/white-stripe/
   surface debris and identify whether it belongs to the shell, Casilda, or an
   Activity. Normalize the boundary, not every Activity's internal design.
3. **SHELL-STATE:** prove Home and Frame transition through launching → active →
   stopped from authoritative lifecycle state, including abnormal exit.
4. **SHELL-INPUT:** prove pointer/keyboard routing on one representative
   Activity, then reuse the semantic path; do not multiply per-Activity hacks.
5. **SHELL-A11Y:** inspect representative Home, Frame, Journal, Help, and one
   Activity for names, roles, and deterministic focus.

## Execution rule

After each shell-wide fix, re-run the launch matrix and update only the rows
whose evidence changed. Promote an Activity from FUNCTIONAL PORT only when its
own task list has evidence. Keep visual normalization deferred unless a concrete
shell boundary bug blocks usability or GTK3 retirement.
