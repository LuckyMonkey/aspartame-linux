# GTK4 activity matrix

No activity is marked usable until it launches inside a running GTK4 Sugar session.

| Activity | Pinned head | Import/build | Launch/toolbar/palette/Journal/clipboard/quit |
|---|---|---|---|
| Calculate | `1ff50e7` | not yet tested | not tested |
| Log | `b4c43c4` | not yet tested | not tested |
| Browse | `c448927` | not yet tested | not tested |
| ImageViewer | `87fedc0` | not yet tested | not tested |
| Terminal | `1425071` | not yet tested | not tested |


Home shell note (2026-09-02): Favorites/Home and the search List View render in
the pinned preview. The search path was exercised semantically and returned to
Home without a traceback. It correctly has no matches because these Activity
sources have not yet been built, installed, or registered as preview bundles.


## Porting gate

Use [GTK4_ACTIVITY_RUNBOOK.md](GTK4_ACTIVITY_RUNBOOK.md) for each Activity.
The columns are deliberately separate: a source checkout that imports is not
a launchable Activity, and a process that stays alive is not a completed
lifecycle.

An Activity moves from **source only** only after the following evidence exists:

- isolated import/build result at the pinned source SHA;
- Home activation inside the running GTK4 preview;
- private `org.laptop.Activity<SUGAR_ACTIVITY_ID>` D-Bus name and object path;
- Wayland first paint through Casilda;
- toolbar/palette behavior and the canonical Stop action;
- clean bus-name release and process exit;
- relaunch/resume evidence when the Activity owns persistent state.

The first target remains Log because it already exercises the shell's Activity
launch path and exposes the current service-registration blocker. Do not
parallelize the next five ports until one Activity passes this gate.
