# Settings and packaging proposals — code review, 2026-10-22

These findings come from reading source and patches, not new runtime checks.
The user requested code research and proposals without test/build expense.
Prior guest observations remain in `reports/gtk4/settings-lifecycle-20261022.md`.

## Priority 1: Stop Settings from redirecting section keyboard input

Evidence: upstream-derived `jarabe/controlpanel/gui.py`,
`ControlPanel.__key_press_event_cb`, together with
`patches/gtk4-preview/0164-controlpanel-escape-capture.patch` (look up the
0164 filename in the patch directory; the number identifies the change).
The handler ends by grabbing the main toolbar search entry whenever it does
not have focus. Patch 0164 moves this entire handler to CAPTURE phase.
That means ordinary keys are intercepted before the focused section widget
handles them. The search toolbar is not the active toolbar inside a section.
This is a plausible cause of broken keyboard activation or section editing;
it does not explain the failed pointer-based About probe by itself.

Proposal: use a small capture handler only for explicit navigation keys.
Keep search/type-ahead handling on the main Settings page and avoid moving
focus for ordinary events. Preserve section cancel/undo on Escape and the
existing one-result Enter behavior. Do not consume Tab/Shift+Tab.
Later acceptance: keyboard navigation among tiles, section text entry,
Escape from a section, and Escape from the main panel.

## Priority 1: Give all shell navigation one Settings dismissal contract

Evidence: `0203-canonical-go-home-action.patch` defines `actions.go_home()`
without closing Settings. D-Bus `ShowHome()` closes Settings before delegating,
but the main-window F3 handler and toolbar menu call `actions.go_home()`
directly. Therefore the alleged canonical action has caller-dependent modal
cleanup. `0102-shell-navigation-closes-control-panel.patch` adds cleanup to
several actions, while `ShowJournal()` is outside that cleanup patch.
The October 17 packaged service also contained duplicate `ShowNeighborhood`
and `ShowGroup` definitions; later Python definitions override earlier ones,
including cleanup added to the earlier definitions.

Proposal: put panel ownership/dismissal in one shell-owned lifecycle helper,
used by semantic Home, Neighborhood, Group, Journal, Frame and direct UI
navigation. Preserve section apply/cancel semantics. Eliminate duplicate
method definitions in the exported source, not just the first matching block.
Do not infer the packaged result from grep finding a method somewhere.
Later acceptance: open Settings, invoke each supported navigation route,
then reopen Settings and inspect modal ownership.

## Priority 1: Bound About inventory work and collect it once per refresh

Evidence: `gtk4-overlay/src/cpsection/aboutcomputer/inventory.py`,
`command_output()` calls `subprocess.check_output()` without timeout.
`collect_inventory()` invokes `lscpu` and `lspci`. `model.get_build_number()`
collects the entire inventory merely to return a build string, and
`get_aboutcomputer()` calls it again. The control panel's `ModelWrapper._setup()`
eagerly calls all `get_*` methods, then the view calls these getters again.
`AboutComputer._refresh_system()` performs collection synchronously during
construction and on button click. A slow command can block the shell UI;
opening a section also repeats work unnecessarily.

Proposal: read build identity directly from os-release, add bounded command
timeouts and handle TimeoutExpired, collect one snapshot per user refresh,
and deliver optional probes asynchronously to the GTK main loop. Keep
widget updates on that loop, discard results after the view closes, and
keep the Refresh button stable so refresh does not destroy keyboard focus.
Avoid treating read-only getters as a generic settings undo snapshot.
Later acceptance: unavailable and slow command paths, repeated refresh,
close while collecting, stable focus, and normal labeled inventory.

## Priority 1: Make exported runtime freshness explicit

Evidence: `scripts/build-iso.sh` extracts an external preview archive,
updates overlay/native Activity files and selected scripts, but does not
replay the whole current shell/toolkit patch series. It applies selected
repairs (About registration and Settings ownership). `STANDALONE-MANIFEST`
records only the input archive hash, even though staging then changes code.
This permits a fresh ISO to contain current views and older shell behavior.
The October 17 packaged source observed in the prior session lacked the
retention/return lines in patch 0058 and contained duplicate navigation methods.

Proposal: define the archive's pinned source/patch contract and include a
source revision plus overlay/helper/patch manifest for the final staged
runtime. Rebuild/export when required shell/toolkit changes are absent.
Keep explicit repair migrations for supported older archives rather than
accumulating silent partial backports. Do not replay all patches blindly
onto an already patched archive.
Also package `sugar-gtk4-settings-probe.py` in the helper list: it currently
requires manual copying despite being the new acceptance entrypoint.

## Priority 2: Make tile activation accessible without pointer synthesis

Evidence: `0099-controlpanel-section-accessibility.patch` gives `_SectionIcon`
a BUTTON role, label, focusability and Enter/Space handling. The base widget
is still a `Gtk.Box` with a gesture controller; assigning an accessible role
is not an exported activation action. Prior guest probing found no AT-SPI
action on the named About target. The probe searches by name only and could
select the child label rather than the tile, which must be distinguished
before blaming the widget implementation.

Proposal: prefer a real `Gtk.Button` containing the icon and label, preserving
Sugar styling and the existing option-clicked routing. Alternatively implement
the GTK-supported accessible activation contract. In the probe, match role
and supported action in addition to name. Record the selected object's role,
parent, and bounds if activation fails. Do not treat an injected mouse-event
request returning as proof that a click reached the intended widget.

## Priority 2: Finish Activity Manager semantics before claiming GTK4 parity

Evidence: `gtk4-overlay/src/cpsection/activities/view.py` has no face rating
control; its action button accessible name is only the repeated action label.
The root TODO's checked face-rating entries describe earlier GTK3 work, not
an implemented GTK4 equivalent. `_remove_clicked()` invokes approval and
removal synchronously; model.py uses blocking subprocess.run for both.
`undo()` only reloads rows, so section Cancel does not reverse removal.
Quarantine exists, but there is no restore action in this GTK4 view.
`MANAGED_ROOTS` omits `/usr/lib/aspartame/gtk4-preview/prefix/share/sugar/activities`;
packaged modern bundles can be displayed as User-installed even when they
are neither user-owned nor removable.

Proposal: share the durable rating data contract, add native GTK4 face
controls, give action buttons activity-specific accessible names, distinguish
bundled read-only Activities from user installations, and define immediate
remove/restore semantics explicitly. Move approval/removal work off the UI
thread without bypassing approval. Do not simply whitelist immutable packaged
bundles for deletion; introduce hide/disable state if that is the intended UX.

## Priority 2: Treat patch syntax and application evidence separately

Evidence: patch 0058 had a short hunk count and GNU patch silently ignored
its final added lines. Other reviewed examples include 0099's final hunk
(declared 6/12 lines, visible 5/11) and 0185's final context after its declared
1/12 hunk. Some files use unprefixed blank context lines, so a naive line
counter over-reports corruption. No comprehensive patch failure count is
claimed from this review.

Proposal: normalize hunk metadata with a parser that handles blank context,
review each changed hunk against its pinned baseline, and make patch fidelity
an explicit build contract. Existing grep-based idempotence checks can accept
partial implementations. Do not mass-edit counts from the preliminary scan
or equate syntactic validity with correct behavior.
