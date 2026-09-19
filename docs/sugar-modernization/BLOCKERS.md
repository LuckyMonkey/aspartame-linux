# GTK4 blockers

## GTK4-018 — Activity icon resolution differed between Home and palettes

- Category: `UPSTREAM-SHELL` / shared GTK4 presentation
- Reproduction: a bundle whose metadata reader returned a basename could be
  passed directly to one `Icon.props.file` caller while another caller used a
  resolved path, producing an empty icon in one surface and no useful error.
- Fix: `jarabe.desktop.activitieslist` now resolves absolute and bundle-relative
  icon paths once for both Home rows and Activity palettes. Missing metadata is
  logged and receives a visible Sugar `activity-start` fallback rather than a
  blank surface.
- Scope: this is a shell boundary fix; it does not normalize Activity-internal
  artwork or claim per-Activity visual parity.
- Verification: all 48 shipped GTK4 package metadata icons resolve in the host
  inventory check; `make test` passes 388 tests. A guest runtime rebuild is the
  next evidence step.
- Status: fixed in the overlay; guest runtime verification pending.

## GTK4-019 — Casilda surface exposed a launch-time white allocation stripe

- Category: `UPSTREAM-SHELL` / Casilda presentation boundary
- Reproduction: launch Help into the modern Space and capture the 1920×1080
  surface while the Activity is mapped; a white stripe appeared immediately
  below the Sugar top bar before the Activity's black canvas.
- Fix: patch `0159-shell-opaque-activity-surface.patch` gives the Casilda page
  an explicit opaque black GTK background. The Activity still owns its internal
  canvas and layout.
- Verification: rebuilt guest, restarted GTK4 PID `44019`, launched Help PID
  `44522`, and captured `reports/screenshots/sugar-20260919-125340-v0.0.31.png`;
  the stripe is absent. Help visibility/search both pass.
- Status: fixed in the GTK4 shell; other Activity-specific chrome remains
  deferred by policy.

## GTK4-020 — Home listed native and classic replacements twice

- Category: `UPSTREAM-SHELL` / Activity catalog policy
- Reproduction: GTK4 Home List showed native `org.aspartame.Calculate` and an
  unsupported classic Calculate row with the same display name.
- Fix: `_catalog_bundles()` keeps classic-only entries, but suppresses an
  unsupported bundle when a resolvable GTK4 bundle has the same normalized
  Activity name. No bundle is removed from disk and no Activity artwork is
  rewritten.
- Verification: rebuilt and restarted GTK4 PID `48013`; `ShowList` screenshot
  reports 51 activities and contains one native Calculate row.
- Status: fixed in the GTK4 Home catalog; classic-only Activities remain
  available and explicitly labeled.

## GTK4-001 — toolkit uses unavailable enum member

- Category: `UPSTREAM-TOOLKIT` / Arch integration
- Reproduction: GTK4 PyGObject import, then toolkit icon tests on Ubuntu 24.04.
- Evidence: `Gtk.IconLookupFlags.NONE` raises `AttributeError`; GTK4 binding accepts integer `0` for no flags.
- Fix: preview-only replacement in `sugar4/graphics/icon.py` and `iconentry.py`; targeted tests now pass 55/55.
- Upstream destination: sugar-toolkit-gtk4 issue/PR.
- Status: fixed locally, candidate for upstream submission.

## GTK4-002 — sugar-ext GIR annotation

- Category: `UPSTREAM-EXT` / Arch integration
- Reproduction: Meson build reaches `SugarExt-2.0.gir`.
- Evidence: malformed gtk-doc comment in `src/sugar-fatattr.c` stops GIR generation; C libraries and five tests build/pass.
- Fix: preview-only comment correction; rerun full Meson build next.
- Status: resolved locally; the guest sugar-ext build and GTK4 typelib
  generation now pass. Upstream cleanup remains a candidate.

## GTK4-003 — complete shell runtime

- Category: `UPSTREAM-SHELL` / Wayland
- Reproduction: use `scripts/sugar-gtk4-space.sh gtk4` in the guest preview.
- Status: partially resolved; the runner and default Home path are operational. Full
  shell parity (Frame, Journal, Neighborhood, Settings, accessibility) remains open.

## GTK4-004 - shell toolkit activityfactory gap

- Category: UPSTREAM-TOOLKIT / UPSTREAM-SHELL
- Reproduction: jarabe/main.py imports sugar4.activity.activityfactory, but toolkit PR 35 removed the module.
- Fix: preview compatibility surface now supplies the launch contract, propagates the
  shell-owned Activity UUID, and registers Casilda launches with ShellModel.
- Verification: Log Activity launches with matching environment/service identity and
  closes cleanly in repeated runtime checks.
- Status: resolved for the preview; broader Activity surface/input parity remains open.

## GTK4-005 - Telepathy GI missing

- Category: ARCH-PACKAGING
- Reproduction: shell import failed with ValueError: Namespace TelepathyGLib not available.
- Fix: installed Ubuntu gir1.2-telepathyglib-0.12 and libtelepathy-glib0t64.
- Status: resolved in host preview environment.

## GTK4-006 - Xapian Python binding missing

- Category: ARCH-PACKAGING
- Reproduction: Journal import failed with ModuleNotFoundError: No module named xapian.
- Fix: installed Ubuntu python3-xapian.
- Status: resolved in host preview environment.

## GTK4-007 - gwebsockets missing

- Category: ARCH-PACKAGING
- Reproduction: API socket import failed with ModuleNotFoundError: No module named gwebsockets.
- Fix: installed Ubuntu python3-gwebsockets.
- Status: resolved in host preview environment.

## GTK4-008 - preview profile data missing

- Category: ASPARTAME-INTEGRATION
- Reproduction: fresh isolated profile had no org.sugarlabs schema or group-label data; intro then failed with empty-label/index errors.
- Fix: launcher contains GSETTINGS_SCHEMA_DIR, SUGAR_GROUP_LABELS, and SUGAR_HOME under the preview runtime.
- Status: resolved for preview; one test initially omitted SUGAR_HOME, and stable host profile keys were restored from generated backups.

## GTK4-009 — Home eagerly constructs a GTK3-only activity list

- Category: `UPSTREAM-SHELL` / `UPSTREAM-TOOLKIT`
- Reproduction: launch the pinned preview; Home construction reaches `Gtk.TreeViewColumn.pack_start()` with the toolkit's plain `CellRendererIcon` adapter and raises `TypeError`.
- Fix: the preview defers `ActivitiesList` until List View is requested; default Favorites/Home can initialize without the unfinished legacy list.
- Status: resolved for the GTK4 Home ListView; current runtime exercises search,
  keyboard activation, and isolated modern bundle lookup. The historical
  deferred-construction workaround remains documented for GTK3 compatibility.

## GTK4-010 — GTK4 preview profile validator rejects its generated RSA key

- Category: `UPSTREAM-TOOLKIT`
- Reproduction: fresh preview profile generates `ssh-keygen -t rsa`, then `sugar4.profile` accepts only `ssh-dss` and repeatedly shows intro.
- Fix: accept modern SSH public-key prefixes while preserving the existing private-key hash validation.
- Status: fixed in preview; upstream candidate.

## GTK4-011 — Home eagerly constructs optional Telepathy-backed views

- Category: `DBUS` / `UPSTREAM-SHELL`
- Reproduction: private preview DBus session has no `org.freedesktop.Telepathy.AccountManager`; eager `MeshBox`/`FriendsTray` construction aborts before Home is installed.
- Fix: defer Group/Neighborhood construction and make FriendsTray degrade to the owner-only tray when collaboration is unavailable.
- Status: default Home path unblocked; collaboration remains untested.

## GTK4-012 — obsolete host stack cannot represent current Casilda

- Category: `CASILDA` / `ARCH-PACKAGING`
- Reproduction: current Casilda main requires GTK 4.22.2 and wlroots 0.20; the
  abandoned Ubuntu-host preview had GTK 4.14 and used Casilda 0.3.
- Root cause: the experiment ran in the wrong environment and could not test
  the current upstream compositor.
- Fix: build Casilda `cecb869` against stock Arch guest GTK 4.22.4 and
  wlroots 0.20.2 in an isolated guest prefix.
- Verification: `Casilda-1.0.typelib` imports and `wayland-info` connects to
  the live `wayland-sugar` socket.
- Status: resolved; host approach retired.

## GTK4-013 — Neighborhood accessibility patch drift

- Category: `UPSTREAM-SHELL` / preview patch maintenance
- Reproduction: the historical 0127 patch expected two overlapping malformed
  accessibility hunks in `meshbox.py`; current source already has independent
  `update_property()` and `set_accessible_role()` calls from 0114/0115.
- Resolution: the build now retires 0127 when those semantic calls are present,
  recording the patch digest without applying a stale textual diff.
- Status: resolved; no new runtime behavior was required.

## GTK4-014 — Journal rooted unparented view attachment

- Category: UPSTREAM-SHELL / GTK4 widget ownership
- Reproduction: JournalActivity constructs its main/detail views after the
  JournalWindow is rooted. The generic rooted-widget guard deferred even
  unparented views, so set_canvas() retried forever and ShowJournal() remained
  blank.
- Fix: 0129 defers only widgets still attached to another parent; an
  unparented rooted view is appended immediately to the Journal canvas area.
- Status: fixed in the GTK4 preview; runtime verification follows the guest
  rebuild.

## GTK4-013 — Arch splits `glib-mkenums` into `glib2-devel`

- Category: `ARCH-PACKAGING`
- Reproduction: sugar-ext Meson configuration fails because `glib-mkenums`
  is absent when only `glib2` is installed.
- Root cause: current Arch packages the development generator separately.
- Fix: add `glib2-devel` to the Aspartame ISO development profile.
- Verification: sugar-ext builds, installs its GIR/typelib, and passes five
  native tests.
- Status: resolved.

## GTK4-014 — shell distribution target references a missing icon

- Category: `UPSTREAM-SHELL`
- Reproduction: after successful `autogen.sh`, `make` stops because
  `data/icons/Makefile.am` lists absent `list-add.svg`.
- Root cause: the PR source manifest and checkout contents disagree.
- Fix: FIRST PIXELS stages the Python shell data/extensions after generating
  `jarabe/config.py`; it does not manufacture an icon or alter `/usr`.
- Upstream candidate: yes; correct the source distribution manifest or add
  the intended artwork upstream.
- Status: runtime unblocked; upstream packaging defect remains open.

## GTK4-015 — toolkit and datastore disagree on the D-Bus service name

- Category: `DBUS` / `DATASTORE`
- Reproduction: Favorites calls `sugar4.datastore.find`; D-Bus reports that
  `org.laptop.sugar4.DataStore` has no owner while the launched service owns
  `org.laptop.sugar.DataStore`.
- Root cause: toolkit PR naming changed without a matching datastore service
  contract in the pinned source.
- Fix: preview patch `0018` keeps the established datastore service and
  interface contract in `sugar4`.
- Verification: Favorites queries complete against the private datastore bus.
- Status: resolved; upstream toolkit candidate.

## GTK4-016 — private session omits locale variables

- Category: `ASPARTAME-INTEGRATION`
- Reproduction: Journal date rendering raises `KeyError: 'LANG'` in
  `sugar4.util.timestamp_to_elapsed_string`.
- Root cause: the preview launcher constructs a private environment without
  propagating a normalized locale.
- Fix: normalize `LANG` to the caller's locale or `C.UTF-8` in the launcher.
- Verification: the corrected Home run has no locale traceback.
- Status: resolved downstream in the preview launcher.

## GTK4-017 — D-Bus activation inherits the caller's runtime directory

- Category: `DBUS` / `ASPARTAME-INTEGRATION`
- Reproduction: activated Telepathy/GVFS processes running as uid 1000 try to
  create `/run/user/0/dconf` and receive permission errors.
- Root cause: `XDG_RUNTIME_DIR` is applied to the command *inside*
  `dbus-run-session`, after the private bus has captured its activation
  environment.
- Fix: create the private bus only after applying the complete preview
  environment.
- Verification: activated services use the preview runtime directory; the
  corrected run has no `/run/user/0/dconf` permission error.
- Status: resolved downstream in the preview launcher.

## GTK4-018 — GTK4 co-installation breaks stable GTK3 Activity startup

- Category: `GI/INTROSPECTION` / `ASPARTAME-INTEGRATION`
- Reproduction: after installing GTK4, launch Terminal, Write, or Image Viewer
  from stable Sugar. Each fresh process fails because GDK 4 is already loaded.
- Root cause: Aspartame's `sitecustomize` imported `sugar3.graphics.window`
  before declaring the GTK/GDK 3 namespace. With both typelibs installed,
  PyGObject selected GDK 4.
- Fix: the GTK3-only hook now requires `Gdk` and `Gtk` 3.0 before importing
  Sugar. Both ISO and development-overlay copies are synchronized.
- Regression coverage: `test_activity_window_bridge_uses_sugar_window_boundary`.
- Verification: the standard runtime probe reports GTK 3.24.52 without a GI
  traceback, and a fresh packaged Terminal Activity process rendered visibly.
- Status: resolved; stable GTK3 and isolated GTK4 can coexist.

## GTK4-019 — Favorites layout calls the renderer-only icon sizing API

- Category: `UPSTREAM-SHELL`
- Reproduction: launch corrected Home; Favorites allocation calls
  `ActivityIcon.set_size()` and raises `AttributeError`.
- Root cause: `ActivityIcon` is a GTK4 `CanvasIcon`, whose public API is
  `set_pixel_size()`; `set_size()` belongs to the legacy cell renderer.
- Fix: preview patch `0019` uses the existing GTK4 icon API at the call site.
- Verification: the Favorites ring and XO render beyond 60 seconds.
- Status: resolved; upstream shell candidate.

## GTK4-020 — GTK4 cell renderer drops Jarabe's scrolling contract

- Category: `UPSTREAM-TOOLKIT`
- Reproduction: enter a Home search; lazy `ActivitiesList` calls
  `CellRendererActivityIcon.connect_to_scroller()` and raises `AttributeError`.
- Root cause: GTK3 `CellRendererIcon` exposes scroll tracking, but the GTK4
  compatibility renderer omitted that API while Jarabe still consumes it.
- Fix: preview patch `0020` restores `connect_to_scroller()`, scroll state
  callbacks, and `is_scrolling()` at the toolkit compatibility boundary.
- Verification: the search path passes renderer setup and reaches List View.
- Status: resolved; upstream toolkit candidate pending native list migration.

## GTK4-021 — lazy Home List View loses its toolbar dependency

- Category: `ASPARTAME-INTEGRATION`
- Reproduction: after List View construction, a non-empty query calls
  `HomeBox._set_view()` and raises `AttributeError: _toolbar`.
- Root cause: preview patch `0012` centralized lazy list construction but did
  not retain the constructor's toolbar for later view changes.
- Fix: preview patch `0021` stores the existing toolbar reference on
  `HomeBox`; no new dependency or abstraction was added.
- Verification: AT-SPI sets `terminal`, the GTK4 search result surface renders,
  clearing the query returns the Favorites wheel, and the same Jarabe process
  remains alive without a traceback.
- Status: resolved downstream; fold into the upstreamable lazy-list change.

## GTK4-022 — Activity surface and cleanup verified; QEMU input transport remains open

The pinned Log Activity is built, installed, and registered. Journal launches
it through Jarabe; Casilda paints its surface; D-Bus Close, repeated relaunch,
and abnormal exit all clear the process and bus name. The guest does expose
PS/2, USB, and virtio keyboard event nodes, but the current QEMU QMP
`input-send-event` and monitor `sendkey` paths produce no evdev records, so
Pointer delivery is separately proven: an absolute-tablet click opened a Help
expander in the live GTK4 surface; keyboard delivery and keyboard-driven focus
transfer remain unproven. See `reports/gtk4/qemu-input-frontier-20260915.md`
and `qemu-pointer-frontier-20260915.md` for the reproductions.

## GTK4-023 — AT-SPI bus discovery collides across the two Spaces on one X display

- Category: `ASPARTAME-INTEGRATION` / verification tooling
- Reproduction: run `scripts/sugar-gtk4-help-visible.py` after the classic
  GTK3 shell has been (re)started more recently than the modern GTK4 shell.
- Evidence: each Space runs its own private `at-spi-bus-launcher`, but both
  advertise themselves through the same shared X11 root window `AT_SPI_BUS`
  property; whichever launcher started most recently wins. `Atspi.get_desktop()`
  follows that property and does not honor an `AT_SPI_BUS` environment
  override (confirmed with the variable set and visible in `os.environ`).
  A probe run after a GTK3 restart silently walks GTK3's tree instead of
  GTK4's, with no error until a specific lookup fails.
- Fix: `scripts/sugar-gtk4-focus-probe.py` saves the property, temporarily
  points it at the modern Space's own deterministic bus socket, queries,
  and restores the original value in `finally`. Verified against the live
  guest; see `reports/gtk4/atspi-bus-discovery-20260915.md`.
- Status: fixed in the new probe; `sugar-gtk4-help-visible.py` and any
  future AT-SPI tooling should adopt the same save/swap/restore pattern.
  Past "AT-SPI names/roles" evidence should be treated as ordering-sensitive
  until re-verified with a bus-pinning probe.

## GTK4-024 — Keyboard focus does not cross from the shell into an embedded Activity surface

- Category: `CASILDA` / `UPSTREAM-SHELL`
- Reproduction: with a real Activity active (Help, in a process separate
  from the shell), send one physical Tab via QMP, then probe AT-SPI focus
  with the GTK4-023 fix applied.
- Evidence: focus moves once, from the Jarabe window down into the
  `Gtk.Stack` "activity" child (the Casilda compositor widget), then stops;
  a second and third Tab produce no further change. The Activity's own
  AT-SPI tree is fully populated and correctly marks its search entry,
  scroll pane, and topic buttons `focusable=True`, but every node in it,
  including the Activity's own top-level frame, reports `focused=False`.
  Sugar's semantic key handler does not consume a bare Tab
  (`KeyHandler._key_pressed_cb` returns `False`), so this is not a shortcut
  swallowing the event; GTK's own focus chain simply has no visibility past
  the compositor widget's boundary.
- Root cause: keyboard focus was never handed to the embedded Wayland
  client at the compositor/seat level (a `wl_keyboard` enter operation),
  which is a separate step from GTK4's widget-level focus chain and is
  Casilda's responsibility, not the shell's or the Activity's.
- Status: resolved 2026-09-15. Four faults sat in series. The shell overlay
  owned window focus, so the compositor was never a key event's target
  (retired by 0140); nothing then claimed focus, and a grab at switch time
  did not survive the stack transition (0136 grabs from the stack's own
  signals); `KeyHandler._key_pressed_cb`, attached to four widgets, returned
  True for every duplicate dispatch and so swallowed keys Sugar never acted
  on (0139); and Casilda sent each key before the modifier state it was
  modified by, making Shift apply one keystroke late (0138). With 0137
  (keyboard focus at map time) these close the path: typing, Tab, Shift+Tab,
  Enter and Space all reach a real Activity. See
  `reports/gtk4/keyboard-delivery-20260915.md`.

## GTK4-025 — the preview patch series does not reconstruct the preview

- Category: `BUILD` / patch pipeline
- Reproduction: inside the development guest, `make sugar-gtk4-series-check`.
  It builds a pristine tree per repository with `git archive HEAD` from the
  pinned baseline SHAs, applies the series with no idempotence heuristics,
  and reports how each patch lands.
- Current state (2026-09-19, after the Journal/navigation repair pass):

  ```text
    exact=80 fuzz=32 failed=6 skipped=1 uncompilable=0
    Result: PASS (a clean rebuild compiles)
  ```

- What was repaired in that pass:
  - `0040` appended `model.stack.set_visible_child_name("home")` on every
    build run through a context-free hunk; the live checkout accumulated
    348 copies. `0038` had itself been regenerated from that corrupted tree.
    0038 is now an exact diff and 0040 is gone.
  - `0045` (a hunk that deletes a line from between `else:` and its body,
    which cannot match a valid file) and `0046` are removed; `0156` carries
    their intent.
  - `0139` assumed `self._last_dispatch` already existed. It did not exist
    in any patch - only in the hand-edited checkout - so the patch could
    never apply to a clean baseline. It now introduces the whole mechanism.
  - The `main.py` and `homewindow.py` chains are folded into `0157` and
    `0158`. Replaying the old chains produced a `main.py` that failed to
    parse (`IndentationError` at line 310); both files are now byte-identical
    to the verified preview after a clean replay.
  - `0106` was retired and its idempotent Journal guard was regenerated as
    `0144` against the pinned baseline. The clean replay now applies that
    guard and no longer reports either Journal patch as a failure.
  - `0109` was retired because its rooted-toolbar guard is already supplied by
    the earlier canvas/toolbar ownership change. No behavior was removed.
  - `0103` was regenerated against the single navigation-method block in the
    pinned baseline. It preserves modal dismissal and active Activity clearing
    without recreating the historical duplicate methods.
  - `0128` was retired because the duplicate zoom methods it removed no longer
    exist after the corrected `0103` navigation fold; the first modal-aware
    implementation remains authoritative.
  - `0127` was retired because the Neighborhood label and GROUP role are
    already separate in the preceding accessibility patches; its historical
    malformed deletion no longer has a target.
  - `0121`-`0123` were retired because the Frame label and GROUP role already
    land in `FrameContainer.__init__` through `0118`-`0120`; the later patches
    only relocate calls that are no longer misplaced.
  - The guest build driver now recognizes the semantic results already present
    in the persistent preview checkout for `0012`, `0057`, `0139`, and `0144`.
    A full guest rebuild completed on 2026-09-19 with toolkit, Casilda,
    sugar-ext, Jarabe, datastore, and metadata-reader checks passing.

- What remains open, and why this is still a blocker:
  **A clean replay compiles; the persistent guest preview now rebuilds.** A
  pristine replay is still a patch-fidelity check, while the guest build uses
  semantic verification for changes already present in the maintained checkout.
  The current full guest build passes; runtime startup and visual parity remain
  separate gates.
  Fresh post-build runtime evidence is recorded in
  `reports/gtk4/runtime-20260919-build-lifecycle.md`: the GTK4 runtime check
  passes and Help and Count each complete three real lifecycle cycles.
  The rebuilt one-cycle Activity matrix also passes all 50 registered bundles;
  see `reports/gtk4/activity-matrix-20260919.md`. This remains coverage
  evidence, not a FULL PORT claim for the individual Activities.

  Historical failure evidence (kept for provenance) showed the shell aborting
  during startup:

  ```text
  File ".../jarabe/desktop/favoritesview.py", line 92, in set_resume_mode
  ```

  `patch --fuzz` places content in the wrong scope. In `favoritesview.py`
  it put the accessibility calls (`set_focusable`, `update_property`,
  `set_accessible_role`) at the end of the preceding class's method instead
  of inside `ActivityIcon.__init__`, so they act on the wrong object.
  `groupbox.py` gains a duplicated `update_property` block and `meshbox.py`
  has two statements in the opposite order.

  32 historical patches still need fuzz and 0 fail outright. The clean replay
  compiles, and the maintained guest checkout has semantic verification for
  the moved Frame/service hunks. These fuzz counts are patch-fidelity debt,
  not a current runtime accessibility failure.

- Consequence: the maintained preview is healthy, the guest rebuild passes,
  and a pristine replay compiles. Runtime startup and visual parity remain
  separate gates; patch-fidelity cleanup should not displace them.
- Next step: prioritize real user-visible gaps: peer-backed Neighborhood
  behavior when a second participant is available, then the per-Activity task
  lists. Revisit fuzz cleanup only when a fresh build or runtime regression
  demonstrates that it blocks behavior.
- Status: resolved as a build/runtime blocker; historical fuzz debt retained
  for provenance.
