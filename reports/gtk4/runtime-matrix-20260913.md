# GTK4 runtime matrix — 2026-09-13

Fresh guest evidence from the 1920×1080 QEMU display after commit 1062ed8:

| Area | Evidence | Status |
| --- | --- | --- |
| GTK4 shell/Home | `sugar-20260913-095000-v0.0.31.png` | PASS: fullscreen Sugar Home renders |
| GTK4 startup/import | `sugar4 clean import`; preview build PASS | PASS |
| F-key delivery | QMP `input-send-event` helper; shell logs semantic key probes | PASS: delivery reaches shell |
| Journal | F5 exposes datastore startup failure during Journal initialization | BLOCKED at current frontier |
| Datastore contract | `get_uniquevaluesfor` was sending `a{ss}` to declared `a{sv}` | FIXED in 0083; rebuild applied it |
| Frame/zoom/Spaces | semantic handlers present; fresh visual pass pending datastore stabilization | UNVERIFIED this run |

The largest user-visible difference is therefore not key routing: it is the
datastore service disconnect during Journal setup. The next runtime pass must
capture the datastore process exit and then verify F5 Journal, F6 Frame, F1–F4
zoom views, and F7/F8 switching against GTK3.
