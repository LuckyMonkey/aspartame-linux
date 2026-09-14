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

Journal model contract (2026-09-13): the GTK4 ListView now returns itself from
`get_model()` and implements the legacy action surface (`__len__`, metadata
lookup, set-selected, select-all, and select-none). This reconnects existing
Journal batch toolbar actions without introducing a second datastore model.

Semantic Home navigation (2026-09-14): the fresh GTK4 shell accepted
`org.laptop.Shell.ShowHome` and returned `(true,)`. A 1920x1080 capture shows
the full Favorites ring, XO identity, Home search, and Sugar top bar:
`reports/screenshots/sugar-20260913-234522-v0.0.31.png`.

Journal model runtime reload (2026-09-14): after restarting only the modern
Space, the authoritative runtime check passed for GTK4 PID `44518` on desktop
`1`. Two fresh Journal→Help launch/stop cycles completed with distinct PIDs
`44876` and `44897`; both returned `stop=(true,)` and cleanup PASS.

Semantic navigation round-trip (2026-09-14): on the same fresh GTK4 session,
`ShowJournal`, `ShowFrame`, and `ShowHome` each returned `(true,)` in sequence.
The final Home capture remained 1920x1080 with the Favorites ring and Sugar
top bar: `reports/screenshots/sugar-20260913-234755-v0.0.31.png`.

Spaces regression (2026-09-14): the classic Space check passed with GTK3 PID
`33761` on desktop `0`; the modern Space was then restored and passed with
GTK4 PID `44518` on desktop `1`. Both checks observed their expected active
window and retained distinct shell processes.

Native Home List activation (2026-09-14): `org.laptop.Shell.ShowList` returned
`(true,)` on a fresh GTK4 process (`50899`). The 1920x1080 capture now shows
the native GTK4 activity rows with normalized icons, summaries, versions, and
running-state controls rather than the legacy TreeView list:
`reports/screenshots/gtk4-home-list-native-20260914.png`. The root cause was
package discovery: the overlay desktop package had no `__init__.py`, so the
legacy `jarabe.desktop.activitieslist` remained authoritative. Adding the
package marker activated the overlay; the GTK4 runner also now excludes the
GTK3-only `sugar-overlay/src` path to preserve the hard GI process boundary.

Control Panel runtime (2026-09-14): `org.laptop.Shell.ShowControlPanel`
returned `(true,)` on the same GTK4 process. The live 1920x1080 capture shows
the black Sugar settings surface with About Me, Computer, Background, Backup,
Date & Time, Frame, Keyboard, Language, Modem, Network, Power, Software Update,
and Web Services tiles: `reports/screenshots/gtk4-settings-native-20260914.png`.

Modal navigation cleanup (2026-09-14): opening Settings followed by
`ShowList` now dismisses the modal Control Panel and reveals the native Home
List immediately. The live capture contains the dark Sugar toolbar and native
activity rows, with no Settings surface remaining:
`reports/screenshots/gtk4-modal-dismiss-list2.png`. The fix also covers Home,
Frame, Group, Neighborhood, and both duplicate legacy navigation definitions.
The startup regression encountered during verification was traced to a
comment embedded inside a backslash-continued `env` command; moving that
comment outside the command restored GTK4 process startup. The controller now
allows 30 seconds for cold portal/AT-SPI startup before declaring failure.

Home List accessibility (2026-09-14): after restarting the modern Space, the
AT-SPI tree exposed the installed-activity list as role `list` with label
`Installed activities`; its first Activity row exposed role `button` and a
descriptive accessible name containing the Activity name, favorite view,
summary, version, and actions. This verifies the row semantics against the
live GTK4 bridge, not only source-level assertions. The visible list evidence
is `reports/screenshots/gtk4-home-list-native-20260914.png`.

Home List launch (2026-09-14): a real pointer click on the Help row launched
the GTK4 Help Activity (`activityinstance` PID 63907, activity id
`38d41ee5ec5749af9943383fe81ac79b`) from the native list. The Activity process
was visible while running, then `org.laptop.Shell.StopActivity` returned
`(true,)`; the process exited and the list returned to its stopped state.
Running and stopped captures are recorded at
`reports/screenshots/gtk4-home-list-help-running-20260914.png` and
`reports/screenshots/gtk4-home-list-help-stopped-20260914.png`. The launch
failure was a stale call to the removed `sugar4.activity.activityfactory`
`supports_bundle`/`explain_unsupported` helpers. The overlay now resolves
capability through the existing `get_command()` API, preserving the original
Classic-Space fallback without adding a new launcher service.

Repeated native-list lifecycle (2026-09-14): three additional launches from
the GTK4 Home List/Jarabe Journal boundary completed with distinct Activity
PIDs `64033`, `64055`, and `64077`. Each launch returned `(true,)`, each
`StopActivity` returned `(true,)`, and every child process disappeared within
the cleanup check. An abnormal-exit pass then launched PID `64104`, sent
`SIGKILL`, and confirmed no Help Activity process remained. This extends the
existing Journal lifecycle evidence to the newly repaired Home List launcher
without changing Casilda or introducing another lifecycle abstraction.

Journal-to-Neighborhood navigation (2026-09-14): runtime evidence exposed a
real shell-view bug: after `ShowJournal`, `ShowNeighborhood` changed the zoom
level but left the synthetic Journal activity marked active, so the Journal
surface remained underneath a dim Neighborhood overlay. The navigation patch
now clears the active Journal target before entering Home, Group, Neighborhood,
or the Home List. After rebuilding and restarting the modern Space,
`ShowJournal` followed by `ShowNeighborhood` produced a clean full-surface
Neighborhood view with its explicit empty state and no Journal rows beneath it:
`reports/screenshots/sugar-20260914-004707-v0.0.31.png`.

Spaces regression after the navigation rebuild (2026-09-14): the guest
runtime check passed for GTK4 PID `66777` on desktop `1`, switched to GTK3 PID
`33761` on desktop `0` and passed there, then returned to GTK4 and passed
again. This confirms the active-activity clearing change did not damage the
classic Space or the semantic modern/classic workspace boundary.

Journal search input (2026-09-14): with the GTK4 Journal active, a QMP pointer
click focused the native search entry and real USB-keyboard events entered
`help`. The list visibly changed from 46 entries to `33 matches for “help”`;
four Backspace events then restored the unfiltered Journal. Captures are
`reports/screenshots/sugar-20260914-005132-v0.0.31.png` and
`reports/screenshots/sugar-20260914-005141-v0.0.31.png`. This is runtime input
evidence through the QEMU path, not a model-only test.

Journal resume/open (2026-09-14): a QMP pointer activation on a filtered
Journal row resumed the existing GTK4 Help Activity (PID `67597`, activity id
`38d41ee5ec5749af9943383fe81ac79b`). `StopActivity` returned `(true,)` and the
process cleanup check passed. This verifies the native row activation path in
addition to search filtering and clearing.

Keyboard frontier (2026-09-14): QMP F1/F3 events sent while the Journal search
surface had focus produced no visible zoom transition, although the equivalent
semantic D-Bus actions remain reliable. The modern shell stayed alive with no
fatal traceback. This remains an input-routing gap to address after the
user-visible Journal behavior, not evidence to expand the Spaces machinery.

Journal detail re-entry stability (2026-09-14): repeated live cycles of
`ShowJournal` → pointer activation of a Journal row → `Escape` initially
aborted the GTK4 shell in `gtk_widget_root()` while swapping the detail and
main canvases/toolbars. The root causes were duplicate Escape delivery and a
stale rooted widget during synchronous GTK4 reparenting. The preview now makes
main-view restoration idempotent, routes detail Escape through the shared
keyhandler, and defers only transient canvas/toolbar reattachment until the
next GLib dispatch turn. After a clean guest rebuild, five consecutive live
cycles completed and the shell remained registered (`detail-reentry=PASS`),
with no fatal GTK assertion in the new log. No new lifecycle or Spaces
abstraction was introduced.

Global F-key recheck (2026-09-14): the deployed GTK4 process exposed no
`SugarExt.KeyGrabber` symbol in the GTK4 SugarExt 2.0 typelib. The workspace
grabber consequently raised an AttributeError from its timer and could not
provide physical F1–F6 capture; direct semantic shell actions remain reliable
and native GTK controllers remain intact. The unavailable global-grabber patch
is retired rather than adding a new X11/input dependency. Physical F-key parity
remains PARTIAL and is deferred as a platform/API gap.

Settings navigation (2026-09-14): a live `ShowControlPanel` call opened the
native GTK4 dark Settings grid; a QMP pointer click entered the About Me
section, and the Sugar top-bar stop/close control returned to the grid. This
proves section activation and return behavior, not just initial rendering.
Captures: `reports/screenshots/gtk4-settings-grid-live-20260914.png`,
`reports/screenshots/gtk4-settings-aboutme-live-20260914.png`, and
`reports/screenshots/gtk4-settings-return-live-20260914.png`.

Runtime cleanup after F-key retirement (2026-09-14): the deployed guest had
retained an earlier invalid global-grabber block even after its patch was
retired, so a targeted cleanup patch removed that block from the persistent
preview source. After rebuild and restart, `sugar-gtk4-runtime-check.sh gtk4`
returned `runtime-check=ok` with exactly one GTK4 shell (PID `110330`) on
desktop 1 and the GTK3 process still present. No new timer traceback was
reported. This keeps the known physical F-key limitation explicit while
restoring clean modern-shell startup.

GTK4 clipboard transfer (2026-09-14): under the live GTK4 display, a real
`Gdk.Display.get_default().get_clipboard()` provider was set with
`Gdk.ContentProvider.new_for_bytes("text/plain", ...)`; asynchronous
`read_text_async()` returned the exact marker `aspartame-gtk4-clipboard`.
This verifies actual clipboard transfer through the GTK4 display boundary,
not merely construction of a clipboard object.

Journal drag source (2026-09-14): the GTK4 Journal rows now install native
`Gtk.DragSource` controllers with COPY action and a stable UID payload. A
post-build live `ShowJournal` smoke test constructed the rows and kept the
GTK4 shell alive (`journal-runtime=PASS`) without GTK or Python errors. Drop
consumers remain intentionally unchanged; this closes the missing row-source
side of Journal drag/copy without adding a new service boundary.

Spaces regression after Journal DnD work (2026-09-14): the guest runtime
checker passed in GTK4 (`pid=113178`, desktop 1), switched to GTK3
(`pid=33761`, desktop 0), and returned to GTK4 with both checks passing. The
active-window and workspace assertions remained consistent and no duplicate
shell owner appeared.

GTK4 Activity Manager inventory (2026-09-14): the modern Settings grid now
includes an Activity Manager tile. A live pointer activation opened a native
GTK4 inventory showing 34 registry-backed activities with names, versions, and
explicit System-managed/User-installed status. Remove controls are active and
route through the safe user quarantine or fullscreen approval policy. Captures:
`reports/screenshots/gtk4-settings-activity-manager-grid-20260914.png` and
`reports/screenshots/gtk4-activity-manager-inventory-20260914.png`.

GTK4 Activity Manager removal policy (2026-09-14): the live inventory's Remove
controls now invoke the existing model policy. User-owned bundles are moved to
the recoverable quarantine; system-managed bundles invoke the fullscreen Sugar
approval helper and constrained native remover. The controls no longer claim a
future action while silently doing nothing. A destructive live uninstall was
not performed against the installed guest inventory; the policy is covered by
the existing model tests and the new GTK4 section smoke test.

GTK4 Activity Manager runtime restart (2026-09-14): after rebuilding the
overlay, the guest restarted with one modern shell and the runtime checker
returned `runtime-check=ok` (`pid=131421`, desktop 1; GTK3 reference PID
`33761` retained). No live destructive click was performed against the guest's
installed inventory.

GTK4 Journal keyboard traversal (2026-09-14): Journal rows now explicitly
declare GTK4 focusability and activation, so Tab/Shift+Tab can land on rows and
Enter follows the existing `row-activated` → deferred detail path. This is a
presentation-only fix; the datastore and already-proven resume/lifecycle
contracts are unchanged.

GTK4 Journal keep toggle (2026-09-14): each native row now exposes a Keep
check button. Changes pass through `editable_changes` and the existing
asynchronous datastore writer; success and failure are reported in the Journal
status line, and invalid updates restore the prior toggle state.

GTK4 Journal title editing (2026-09-14): each native row now offers an inline
Edit title/Save title control. Non-empty titles use the shared metadata
validation and asynchronous datastore writer, then update the visible row and
status line. Invalid titles remain in edit mode with an explicit error.

GTK4 Journal deletion (2026-09-14): rows now expose a deliberate two-step
Delete/Confirm delete action. Confirmed deletion uses Jarabe's existing
datastore `model.delete` boundary, refreshes the list, and reports failures in
the status line; no direct filesystem deletion is introduced.

GTK4 ObjectChooser (2026-09-14): the modern overlay now provides a native
`jarabe.journal.objectchooser.ObjectChooser` with the classic response and
selected-object-id contract, Journal search, pointer activation, Cancel, and
Escape handling. It reuses the GTK4 Journal ListView and does not import the
GTK3 Wnck/X11 chooser path.

ObjectChooser boundary correction (2026-09-14): the chooser no longer imports
the GTK3 `sugar3.graphics.objectchooser` module even for a filter constant;
that import could load GTK3 into the GTK4 process. The MIME filter token is now
local to the GTK4 module.

GTK4 Journal mounted entries (2026-09-14): rows now explicitly identify
entries whose datastore metadata uses a non-root mountpoint. The external
volume marker is informational and leaves persistence on the existing
`model.write` mounted-entry path; root entries continue to use the D-Bus update
path.

GTK4 Journal project assignment (2026-09-14): each row now exposes Project,
which opens the native GTK4 ObjectChooser. Accepting a selected Journal UID
writes `project_id` through the existing metadata validation/writer path;
Cancel/Escape closes without changing the entry and failures are shown in the
status line.

Project state visibility (2026-09-14): rows now display the assigned project
UID in the Project button label after a successful update, or the neutral
Project label when no assignment exists.

Project persistence correction (2026-09-14): the label and in-memory metadata
now change only from the datastore writer's success callback; failed writes no
longer present an assignment that was not persisted.

ObjectChooser live construction (2026-09-14): under the deployed GTK4 preview
environment (`ASPARTAME_GTK4_PREVIEW=1`, GTK4 GI typelib path, modern overlay
PYTHONPATH, and `GDK_BACKEND=x11`), a real `Gtk.Application` constructed
`jarabe.journal.objectchooser.ObjectChooser` and returned
`objectchooser=constructed None`. This confirms the module can load in a GTK4
process without importing GTK3; pointer selection through an Activity remains
the next end-to-end proof.

Neighborhood accessibility drift correction (2026-09-14): the first
accessibility patch partially landed (label present, role absent) in the
persistent guest source. Follow-up patch 0115 adds the missing GTK4 group role
and the build guard verifies the semantic result.
