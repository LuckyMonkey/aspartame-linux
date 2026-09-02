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
- Status: in progress.

## GTK4-003 — complete shell runtime

- Category: `UPSTREAM-SHELL` / Wayland
- Reproduction: no supported one-command GTK4 session runner is present in this repository yet.
- Status: open; do not claim GTK4 desktop support until shell, Home, Frame, Journal, and activity lifecycle are exercised.

## GTK4-004 - shell toolkit activityfactory gap

- Category: UPSTREAM-TOOLKIT / UPSTREAM-SHELL
- Reproduction: jarabe/main.py imports sugar4.activity.activityfactory, but toolkit PR 35 removed the module.
- Fix: preview-only compatibility surface supplies create_activity_id and set_compositor_fd_getter; create fails explicitly because GTK4 activity launch is not complete.
- Status: unblocks shell startup imports; activity lifecycle remains blocked.

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
- Status: default Home path unblocked; List View remains open.

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
- Status: open; this is the first shell-stability blocker after FIRST PIXELS.

## GTK4-016 — private session omits locale variables

- Category: `ASPARTAME-INTEGRATION`
- Reproduction: Journal date rendering raises `KeyError: 'LANG'` in
  `sugar4.util.timestamp_to_elapsed_string`.
- Root cause: the preview launcher constructs a private environment without
  propagating a normalized locale.
- Status: open; fix in the launcher, not with a shell source workaround.

## GTK4-017 — D-Bus activation inherits the caller's runtime directory

- Category: `DBUS` / `ASPARTAME-INTEGRATION`
- Reproduction: activated Telepathy/GVFS processes running as uid 1000 try to
  create `/run/user/0/dconf` and receive permission errors.
- Root cause: `XDG_RUNTIME_DIR` is applied to the command *inside*
  `dbus-run-session`, after the private bus has captured its activation
  environment.
- Status: open; sanitize the environment before creating the private bus.

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
