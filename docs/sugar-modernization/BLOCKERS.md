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
