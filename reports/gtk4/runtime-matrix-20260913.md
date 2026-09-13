# GTK4 runtime matrix — 2026-09-13

Fresh guest evidence from the 1920×1080 QEMU display after commit 1062ed8:

| Area | Evidence | Status |
| --- | --- | --- |
| GTK4 shell/Home | `sugar-20260913-095000-v0.0.31.png` | PASS: fullscreen Sugar Home renders |
| GTK4 startup/import | `sugar4 clean import`; preview build PASS | PASS |
| F-key delivery | QMP `input-send-event` helper; shell logs semantic key probes | PASS: delivery reaches shell |
| Journal | F5 / `ShowJournal` now renders the native GTK4 Journal list and search bar | PASS: fresh capture `sugar-20260913-100306-v0.0.31.png` |
| Datastore contract | `get_uniquevaluesfor` was sending `a{ss}` to declared `a{sv}`; root-owned Xapian index also blocked startup | FIXED: 0083 plus user-owned runtime |
| Frame | `ShowFrame` renders Sugar Frame chrome and controls | PASS: fresh capture `sugar-20260913-100255-v0.0.31.png` |
| Zoom/Spaces | Semantic `ShowNeighborhood` and `ShowGroup` actions now render dedicated GTK4 views (`sugar-20260913-104603-v0.0.31.png`, `sugar-20260913-104618-v0.0.31.png`); F3 returns Journal → Home. Direct F7/F8 coordinator probes move EWMH workspace 0↔1 | PASS for view stack/actions; physical F1/F2 delivery still needs final evidence |

The datastore failure is resolved in the current runtime: both the shell and
preview datastore remain alive, and Journal now renders. The next pass should
repair the no-op zoom/Space transitions (the probes are reaching the process),
then continue with activity launch/focus parity.
