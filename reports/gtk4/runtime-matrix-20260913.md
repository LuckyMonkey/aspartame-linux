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
| Zoom/Spaces | F3 returns Journal → Home (`sugar-20260913-100430-v0.0.31.png`); F1 from Home produced no visible Neighborhood transition; F7/F8 captures matched | PARTIAL: Home transition works, Neighborhood/Group/Spaces still need parity work |

The datastore failure is resolved in the current runtime: both the shell and
preview datastore remain alive, and Journal now renders. The next pass should
repair the no-op zoom/Space transitions (the probes are reaching the process),
then continue with activity launch/focus parity.
