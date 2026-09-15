# GTK4 blockers

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
- Status: partially fixed. `casilda_compositor_focus_toplevel()` — the only
  caller of `wlr_seat_keyboard_notify_enter()` — was reached from a single
  `xdg_toplevel_map()` branch covering a fresh, plain, non-maximized map. A
  maximized/fullscreen map (every Sugar Activity) and a restored-state map
  both fell through, so only a pointer click could ever establish keyboard
  focus. Patch `0137-casilda-focus-toplevel-on-map.patch` calls it
  unconditionally; `0136-shell-focus-activity-compositor.patch` is the
  shell-side companion. An Activity launched with no pointer and no AT-SPI
  interaction now reports its own default widget focused. Per-keystroke
  delivery into the client is still broken — Casilda's per-widget
  `key_controller` never fires, so `wlr_seat_keyboard_notify_key()` is never
  called. See `reports/gtk4/casilda-keyboard-focus-20260915.md`.
