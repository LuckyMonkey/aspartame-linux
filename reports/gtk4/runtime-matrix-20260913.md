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

The 0089 descendant-capture build is valid and deployed, but fresh runtime
testing still shows the same no-op F1–F4 result. A duplicate GTK4 process was
also found after restart and removed; only one modern shell now owns workspace 1.
Physical F7/F8 round-trips remain intermittent, while direct `gtk3`/`gtk4`
controller commands switch deterministically. This points to global X11 key
grab ownership as the remaining input issue, not a GTK4 view-rendering failure.

Follow-up root-cause correction (2026-09-13): `SugarExt.KeyGrabber` emits
`key-pressed(grabber, keycode, state)`. The GTK4 workspace grabber had declared
an obsolete fourth `event_time` argument, so grabbed keys could be consumed
without dispatch. Patch 0094 now matches the signal contract and resolves key
values through `Gdk.keyval_from_name()` when GTK4 does not expose a `KEY_F*`
attribute. The guest preview rebuild passes and the focused regression suite
passes; a fresh QMP F-key visual recheck remains PARTIAL pending proof that the
native grab reaches the modern shell on this X11 session.

Deployment correction (2026-09-13): the first rebuilds were falsely reported
as applying 0094 because the guest build script treated any existing
`_modern_key_grabber` code as sufficient. The idempotence guard now checks the
three-argument callback and `Gdk.keyval_from_name()` explicitly. After syncing
the patch and guard into `/mnt/aspartame-dev`, the deployed guest source was
verified to contain both changes. F-key visual dispatch remains unproven after
that corrected deployment, so the completion status stays PARTIAL.

Post-rebuild lifecycle regression check (18:50 UTC): two fresh Journal-launched
Help cycles completed with distinct PIDs/Activity IDs and immediate cleanup;
`sugar-gtk4-lifecycle-probe.sh 2` returned `lifecycle-probe=PASS`.

Input boundary probe (2026-09-13): a root reader attached directly to the
guest's `QEMU QEMU USB Keyboard` event node (`/dev/input/event3`) while QMP
`input-send-event` and HMP `sendkey` F5 events were injected. No Linux evdev
events were observed. This moves the remaining F-key defect below GTK4: the
current QEMU input transport is not reaching the guest keyboard device, so
additional GTK shortcut patches would not address the observed failure.

Modern Help visual activation (2026-09-13): the missing `activity-help.svg`
was restored to the live development share. A fresh Journal `LaunchBundle`
now presents the native GTK4 Help Activity with its Sugar top bar, Help icon,
readable English guidance, and canonical stop control; capture:
`reports/screenshots/sugar-20260913-221408-v0.0.31.png`. The Activity was then
stopped through `org.laptop.Shell.StopActivity`, and its process exited.

QEMU transport experiment (2026-09-13): adding `virtio-keyboard-pci` made a
second guest keyboard (`/dev/input/event4`) enumerate, but focused host F5 still
produced no GTK4 navigation. The extra device was removed to avoid duplicate
input ownership; the launcher retains the verified 1600×900 floating viewport.

Help readability update (2026-09-13): the native Help Activity now uses a dark
Sugar surface with a search field, seven keyboard-accessible `GtkExpander`
topics, wrapped selectable guidance, and live match counts. A live guest
capture shows the first topic expanded and a second topic opened by pointer:
`reports/screenshots/sugar-20260913-222656-v0.0.31.png` and
`reports/screenshots/sugar-20260913-222710-v0.0.31.png`.

Spaces regression check (2026-09-13): the guest runtime checker returned
`runtime-check=ok` for GTK3 on desktop 0 and GTK4 on desktop 1 in one round
trip. It reported stable PID 734 and modern PID 7237 with distinct windows;
the modern Space was restored afterward.

Activity lifecycle regression: PASS. The real Journal `LaunchBundle` path now
completed two cycles with distinct Help Activity PIDs and IDs; both StopActivity
calls returned true and cleanup passed. The prior rejection was caused by
duplicate canonical bundle IDs resolving to the GTK3 bundle before the GTK4
entry.

Repeated/abnormal lifecycle: PASS. Three additional launch/stop cycles
completed with distinct process IDs and immediate cleanup. A fourth Help
Activity was then terminated with SIGKILL; no `helpactivity4` process remained
and the GTK4 shell PID stayed alive, demonstrating abnormal-exit cleanup.

Settings and empty Neighborhood evidence (2026-09-13): `ShowControlPanel`
returned `(true,)` and a fresh 1920×1080 capture showed the native dark Settings
grid with Sugar top bar and stop control:
`reports/screenshots/sugar-20260913-224606-v0.0.31.png`. `ShowNeighborhood`
also returned `(true,)`; its previously blank no-peer canvas is now patched to
show a localized empty-state message (`0097-mesh-empty-state.patch`).

After rebuilding and restarting GTK4, `ShowNeighborhood` returned `(true,)`
without traceback and the live capture visibly showed the message and XO owner
icon: `reports/screenshots/sugar-20260913-230041-v0.0.31.png`. The missing
`Gtk` import found during this runtime check is covered by
`0098-mesh-empty-state-gtk-import.patch`.

Guest build frontier (2026-09-13): after synchronizing the development share,
the full preview build passed all staged patches through `0096`, then completed
Casilda, sugar-ext, Jarabe, and datastore metadata validation successfully.

Journal resume evidence (2026-09-13): from the live GTK4 Journal list, a
pointer activation opened the native entry detail surface with Back navigation,
title, description, preview/metadata fields, and action toolbar. Capture:
`reports/screenshots/sugar-20260913-231110-v0.0.31.png`.

Journal result status (2026-09-13): the rebuilt GTK4 list now reports the
current result count above the rows (live capture showed `44 Journal entries`),
and exposes a clear “Journal search unavailable” state if datastore refresh
fails. Capture: `reports/screenshots/sugar-20260913-231339-v0.0.31.png`.

Query feedback (2026-09-13): when the existing Journal toolbar supplies a
non-empty `query`, the same status line now reports `<count> matches for
“<query>”`; clearing the query returns to the total-entry wording. This keeps
search behavior visible without changing the datastore contract.

Group view evidence (2026-09-13): `ShowGroup` returned `(true,)` and the live
GTK4 surface rendered the Sugar top bar, search affordance, XO owner icon, and
the explicit empty state “No friends are nearby yet.” Capture:
`reports/screenshots/sugar-20260913-231633-v0.0.31.png`.

Frame evidence (2026-09-13): `ShowFrame` returned `(true,)`; the live GTK4
Frame revealed its edge controls, activity tray, XO control, navigation arrows,
and device icons over the shell surface. Capture:
`reports/screenshots/sugar-20260913-231708-v0.0.31.png`.

Frame/activity switching evidence (2026-09-13): a real Help Activity launch
produced PID `31170`; Frame then showed the Help icon as the current running
Activity (`sugar-20260913-231752-v0.0.31.png`). StopActivity returned `(true,)`,
the process disappeared, and the subsequent Frame capture cleared the Help
icon (`sugar-20260913-231813-v0.0.31.png`).

Home List result feedback (2026-09-13): GTK4 Home's native activity list now
exposes a visible status line for the installed total and filtered matches
(`N matching activities (of M)`), while retaining the empty-state clear-search
action. Host regression coverage passed and the guest preview rebuild completed
after syncing the overlay. This closes a user-visible GTK3→GTK4 parity gap
without changing the Activity registry or launcher path.

Post-rebuild regression (2026-09-13): the GTK4 shell restarted cleanly on the
modern Space at 1920x1080 (`sugar-20260913-232259-v0.0.31.png`), and two fresh
Journal→Help launch/stop cycles completed with distinct PIDs and immediate
cleanup (`lifecycle-probe.sh 2`: PASS). The authoritative runtime check also
passed for GTK4 PID `28378` on desktop `1`.

Control Panel accessibility (2026-09-13): the GTK4 preview build applied
`0099-controlpanel-section-accessibility.patch` cleanly. Section tiles now
expose Button semantics and activate through Enter, keypad Enter, or Space;
the guest source was verified at lines 623 and 648 after the build.

Journal selection parity (2026-09-13): the GTK4 ListBox view now honors its
`enable_multi_operations` contract, exposes selected Journal UIDs, and
implements select-all/select-none through native GTK4 row selection. The
synced module passes guest Python syntax validation; runtime loading remains
scheduled for the next GTK4 session restart.
