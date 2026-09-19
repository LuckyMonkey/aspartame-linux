# GTK4 Journal shortcut routing — 2026-09-19

The GTK4 `open_search` shell action previously initialized the Journal object
but did not select the visible Journal page. The shell stayed on Home even
though the Journal had been created. Patch `0163-keyhandler-journal-stack-action.patch`
now applies the same semantic contract as `ShowJournal()`:

- select the Journal Activity as the active shell Activity;
- enter `ZOOM_ACTIVITY` with the key event time;
- select the `journal` stack child;
- reveal the Journal view, toolbox, toolbar, and canvas areas.

The full rebuilt guest applied 0163 and completed the GTK4 preview build. The
existing live `ShowJournal()` route still returns `boolean true` and renders
the native Journal surface at 1920×1080. The keyhandler source now contains the
same stack/visibility operations, so it no longer relies on top-level window
reveal semantics.

Physical F5 delivery remains subject to the documented guest evdev/QEMU input
transport limitation; this report does not mislabel the D-Bus equivalent as a
physical-key test. The Frame Journal action remains the direct manual fallback
until that transport is exercised.
