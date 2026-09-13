# GTK4 runtime matrix — 2026-09-13

Fresh guest evidence from the 1920×1080 QEMU display after commit 1062ed8:

| Area | Evidence | Status |
| --- | --- | --- |
| GTK4 shell/Home | `sugar-20260913-095000-v0.0.31.png` | PASS: fullscreen Sugar Home renders |
| GTK4 startup/import | `sugar4 clean import`; preview build PASS | PASS |
| F-key delivery | QMP `input-send-event` helper; fresh VM launched with `grab-on-hover=on` | PARTIAL: F8 switches Spaces; F1–F4 still produce no visible zoom change |
| Journal | F5 / `ShowJournal` now renders the native GTK4 Journal list and search bar | PASS: fresh capture `sugar-20260913-100306-v0.0.31.png` |
| Datastore contract | `get_uniquevaluesfor` was sending `a{ss}` to declared `a{sv}`; root-owned Xapian index also blocked startup | FIXED: 0083 plus user-owned runtime |
| Frame | `ShowFrame` renders Sugar Frame chrome and controls | PASS: fresh capture `sugar-20260913-100255-v0.0.31.png` |
| Zoom/Spaces | Semantic `ShowNeighborhood` and `ShowGroup` actions now render dedicated GTK4 views (`sugar-20260913-104603-v0.0.31.png`, `sugar-20260913-104618-v0.0.31.png`); F3 returns Journal → Home. Direct F7/F8 coordinator probes move EWMH workspace 0↔1 | PASS for view stack/actions; physical F1/F2 delivery still needs final evidence |

The datastore failure is resolved in the current runtime: both the shell and
preview datastore remain alive, and Journal now renders. The QEMU launcher now
defaults to `grab-on-hover=on`; this preserves a floating/resizable window while
ensuring USB keyboard events reach the guest. F8 was re-proven after restart;
F1–F4 remain the next GTK4 input frontier because no view transition is visible
despite the GTK4 window owning EWMH focus.
