# Sugar development on Aspartame

This is the operational map for the Aspartame Sugar shell. Read this before
changing shell code. The reference environment in this document was inspected
live on 2026-08-29 with Sugar 0.121-7, sugar-toolkit-gtk3 0.121-7, GTK 3.24.52,
Python 3.14.7, Metacity 3.58.1, Xorg, and the Aspartame UI v0.0.14 overlay.

## Fast path

```sh
make sugar-info
# Edit files listed by sugar-overlay/files.list.
make sugar-patch-check
make sugar-reload
make sugar-logs
make sugar-screenshot
make sugar-visual-check
```

A visible change is complete only when `make sugar-reload` passes and
`make sugar-visual-check` produces a current guest-display screenshot. The
screenshot is captured by `ffmpeg` inside the VM from `DISPLAY=:0`, copied out
over SSH, and accompanied by OCR text when `tesseract` is available. This does
not use the host Print Screen shortcut and never restarts Sugar.

For a text-bearing change, require a visible marker explicitly:

```sh
EXPECT_VISIBLE_TEXT='Aspartame UI v0.0.16' make sugar-visual-check
```

The command fails if OCR cannot find that text. OCR is evidence, not a perfect
semantic UI test; screenshots still need visual review for geometry, colors,
alignment, and interaction state.

Use this only when X itself or the system-owned session launcher changed:

```sh
make sugar-session-restart
```

That command intentionally ends Xorg, the session D-Bus, Metacity, Sugar, and
running Activities. It does not unmount or format the persistent home volume.

## Clock format settings

The existing native Date & Time Control Panel now includes a `Clock format` text field. It writes the persistent `org.aspartame.clock` GSettings key through the normal Apply/Cancel model. Leave it blank to use the active `LC_TIME` locale with hours and minutes; examples include `%H:%M` and `%I:%M %p`. The Frame clock observes this key and refreshes without restarting Sugar. Invalid strftime formats disable Apply. This is intentionally a text field now; a future drag-and-drop formatter must preserve the same setting boundary and Sugar Frame ownership.


## What starts Sugar

No display manager participates. The live development image uses this chain:

```text
systemd graphical.target
└─ getty@tty1.service
   └─ agetty --autologin aspartame
      └─ login shell reads ~/.bash_profile
         └─ startx
            └─ xinit
               ├─ Xorg :0
               └─ ~/.xinitrc
                  └─ /usr/local/bin/aspartame-x-session
                     ├─ version marker (development-only popup)
                     └─ dbus-run-session
                        ├─ session dbus-daemon
                        └─ /usr/local/bin/aspartame-session
                           └─ /usr/bin/sugar
                              └─ python3 -m jarabe.main
                                 └─ metacity --no-force-fullscreen
```

`getty@tty1.service.d/autologin.conf` supplies autologin. `.bash_profile`
executes `startx` only on tty1. `.xinitrc` is deliberately a stable one-line
launcher; system-owned logic is in `aspartame-x-session`. A migration backs an
older `.xinitrc` up as `.xinitrc.pre-aspartame-system-session` before replacing
it.

The systemd user manager exists, but it does not launch Sugar. Sugar creates a
separate session bus with `dbus-run-session`. The inspected session exported
`DISPLAY=:0`, `XAUTHORITY=/home/aspartame/.Xauthority`,
`XDG_RUNTIME_DIR=/run/user/1000`, and the active D-Bus address. `/usr/bin/sugar`
adds `SUGAR_HOME`, `SUGAR_PROFILE`, `SUGAR_SCALING`, `GTK2_RC_FILES`,
`MC_ACCOUNT_DIR`, and related variables before executing `jarabe.main`.

`jarabe.main` creates the Home window before starting Metacity, then initializes
the Frame, key/gesture handlers, Journal, notifications, collaboration, and
file transfer after a window manager is detected.

## Restart boundaries

`aspartame-x-session` currently supervises a complete Sugar D-Bus island. When
`jarabe.main` exits:

1. `aspartame-session` exits;
2. `dbus-run-session` ends that session bus;
3. `aspartame-x-session` waits one second;
4. a new bus, shell, Metacity process, and Home window are created.

Therefore `make sugar-reload` does not restart Xorg or the tty login, but it is
more than an in-process Python module reload. The live test changed shell PID
7235 to 9039, D-Bus PID 7233 to 9037, and Metacity PID 7387 to 9199 while Xorg
PID 710 remained unchanged.

Persistent state under `/home/aspartame` survives. This includes dconf, the
Sugar profile, Journal datastore, favorites/layout settings, browser data, and
ordinary files. The QEMU data disk is `/dev/vdb`, mounted as ext4 at
`/home/aspartame`.

Whether every independently running Activity survives loss of the old Sugar
session bus has not been validated. Save Activity work before a shell reload.
A full session restart intentionally terminates Activities.

Changes that normally need only `make sugar-reload`:

- `jarabe` Python shell code;
- Home, Frame, Journal-shell, Neighborhood, Group, and shell-local CSS provider
  changes;
- shell startup theme/font logic.

## Opening Settings reliably

Use:

    make sugar-open-control-panel

This launches Sugar's graphical `ControlPanel` class with the live Sugar
shell's `DISPLAY`, Xauthority, D-Bus session, Sugar profile, and extension
path. The extension path is important: Control Panel discovers sections by
importing `cpsection` modules from that path. A direct Python snippet that
constructs `ControlPanel` without this environment can show a blank or
incomplete panel, or fail with `ModuleNotFoundError: cpsection`. The separate
`/usr/bin/sugar-control-panel` command is a command-line settings utility and
prints usage when invoked without options; it is not the graphical launcher.

The Control Panel is an undecorated, centered modal window by design in the
current Sugar implementation. The helper fixes the launch path; it does not
turn that intentional Sugar surface into a conventional settings window.

The helper refuses to launch if the Sugar shell is not running and does not
start a second panel when one is already present. Its guest-side diagnostic
log is `/tmp/aspartame-control-panel.log`.

Changes that require `make sugar-session-restart`:

- `aspartame-x-session`, `.xinitrc`, Xorg, login/session environment, or
  Metacity startup changes;
- changes that must affect every Activity process rather than only the shell;
- recovery from a broken X or session bus.

A wallpaper path or alpha change made through `org.sugarlabs.user.background`
is observed live by `HomeBackgroundBox` and normally needs no restart.

## Authoritative source and generated runtime

There are intentionally two Sugar copies in a development boot, but only one
editing authority:

| Layer | Location | Owner | Edit? |
|---|---|---|---|
| Official package baseline | cached `sugar-0.121-7-any.pkg.tar.zst` | Arch | no |
| Aspartame shell source | `sugar-overlay/src/jarabe/...` | repository | yes |
| Overlay file list | `sugar-overlay/files.list` | repository | yes |
| Baseline identity/hash | `sugar-overlay/UPSTREAM` | repository | update deliberately |
| Generated ISO patch | `patches/sugar/0001-integrated-navigation.patch` | generated from overlay | no direct edits |
| Patch copied into ISO | `archiso/.../usr/share/aspartame/0001-integrated-navigation.patch` | generated | no direct edits |
| Package-installed shell | `/usr/lib/pythonX.Y/site-packages/jarabe` | pacman `sugar` | never live-hack |
| Complete development runtime | `/mnt/aspartame-dev/sugar/src/jarabe` | generated 9p tree | never edit directly |
| Sugar toolkit | `/usr/lib/pythonX.Y/site-packages/sugar3` | pacman `sugar-toolkit-gtk3` | package separately |

At ISO build time, the generated patch is applied to pacman's installed Sugar
files. At live-development time, the official package tree is copied once to
the 9p runtime and every file in `sugar-overlay/files.list` is installed over
it. `PYTHONPATH=/mnt/aspartame-dev/sugar/src` makes that complete regular
Python package win over `/usr/lib`.

This full-package requirement caused the earlier reload failures: copying only
`jarabe/desktop/viewtoolbar.py` did not override the regular packaged `jarabe`
package. Python selected one package root; it did not merge arbitrary loose
subdirectories.

Run this to answer “will Sugar execute the file I edited?”:

```sh
make sugar-info
```

The command prints every important module path without importing nested Sugar
modules or causing their initialization side effects. `make sugar-reload` also
compares SHA-256 manifests between repository files and the 9p runtime.

To modify another existing `jarabe` file:

1. copy the exact file from the verified official package baseline into the
   matching path under `sugar-overlay/src`;
2. add its `jarabe/...` path to `sugar-overlay/files.list`;
3. edit the repository copy;
4. run `./scripts/sugar-patch.sh update`;
5. run `make sugar-patch-check` and `make sugar-reload`.

Do not copy a file from a newer Sugar package into this baseline. Update
`UPSTREAM`, its SHA-256, all overlay bases, and the package version coherently.

## Package provenance

The inspected VM used official Arch packages, not AUR or manually installed
Sugar files:

| Component | Version | Provenance/runtime path |
|---|---:|---|
| Sugar shell | 0.121-7 | official Arch; `/usr/bin/sugar`, packaged `jarabe` |
| sugar-toolkit-gtk3 | 0.121-7 | official Arch; packaged `sugar3` |
| sugar-artwork | 0.121-5 | official Arch; Sugar themes/icons |
| sugar-datastore | 0.121-5 | official Arch; `datastore-service` |
| Metacity | 3.58.1-1 | official Arch; `/usr/bin/metacity` |
| Core Activities | current Arch `sugar-activity-*` packages | official Arch |

Installed Activities included Browse, Terminal, Write, Calculate, Image
Viewer, Pippy, Paint, Jukebox, Read, and Record. Aspartame does not modify
pacman-owned files at runtime. Guest commands installed under `/usr/local/bin`
are Aspartame-owned development infrastructure copied from this repository.

## Sugar concept map

“Shell reload” below means `make sugar-reload`.

| Concept | Implementation | GTK/rendering and dependencies | Reload |
|---|---|---|---|
| Home/window and zoom pages | `jarabe.desktop.homewindow.HomeWindow` | `Gtk.Window`, `HomeBackgroundBox`, `HomeBox`, `GroupBox`, `MeshBox`; listens to `ShellModel.zoom_level_changed` | shell |
| Home content | `jarabe.desktop.homebox.HomeBox` | `Gtk.VBox`; search and resume-mode coordination | shell |
| Favorites/ring/spiral | `jarabe.desktop.favoritesview.FavoritesView`; `jarabe.desktop.favoriteslayout.RingLayout`, `SunflowerLayout` | custom `ViewContainer` allocations; Sugar style sizes | shell |
| Activity icons | `jarabe.desktop.favoritesview.ActivityIcon`, `FavoritePalette` | `CanvasIcon`, Activity bundle SVG, Journal entries, `XoColor` | shell |
| XO/owner icon | `jarabe.desktop.favoritesview.OwnerIcon`; `jarabe.desktop.buddyicon` | Sugar `BuddyIcon`, profile color/state | shell |
| Running/current Activity | `CurrentActivityIcon`; `jarabe.model.shell.Activity` and `ShellModel` | Wnck/X11 window tracking and Activity metadata | shell |
| Launch/resume | favorites/Home callbacks, `jarabe.model.shell`, Sugar activity factory and Journal object IDs | D-Bus, Journal datastore, bundle registry, X11 | shell; Activity process is separate |
| Home search | `jarabe.desktop.viewtoolbar.ViewToolbar` and `HomeBox` query callbacks | `IconEntry`, delayed GLib search callback | shell |
| Aspartame clock | `jarabe.desktop.viewtoolbar.ViewToolbar` | native `Gtk.ToolButton`/internal `Gtk.Label`; local scoped CSS provider; locale-aware persistent `org.aspartame.clock` format plus locale-aware `datetime.now()` | shell |
| Frame | `jarabe.frame.frame.Frame` | four `FrameWindow` panels, trays, animator, palettes | shell |
| Frame activation | `jarabe.frame.eventarea.EventArea`; `jarabe.view.keyhandler.KeyHandler` | invisible edge/corner X windows; `org.sugarlabs.frame`; F6 calls `Frame.notify_key_press()` | shell |
| Frame navigation | `jarabe.frame.zoomtoolbar.ZoomToolbar` | Sugar toolbar/radio buttons; emits zoom levels | shell |
| Journal | `jarabe.journal.journalactivity.JournalActivity`, `JournalActivityDBusService` | Sugar `Window`; `org.laptop.Journal`; datastore service | shell; data persists |
| Group | `jarabe.desktop.groupbox.GroupBox` | friends model and `BuddyIcon` objects in `ViewContainer` | shell |
| Neighborhood | `jarabe.desktop.meshbox.MeshBox`; `jarabe.model.neighborhood.Neighborhood` | NetworkManager observer plus legacy Telepathy collaboration objects; Snowflake layout | shell |
| Palettes | `sugar3.graphics.palette`, `palettewindow`, shell palette subclasses | GTK windows/menu widgets, Sugar CSS names, some custom drawing | shell/Activity restart |
| Notifications | `jarabe.model.notifications.NotificationService`; `jarabe.frame.notification` | `org.freedesktop.Notifications`, Frame notification windows/icons | shell |
| Settings | `jarabe.controlpanel.gui.ControlPanel` and section modules | GTK, GSettings, D-Bus/system backends | shell for shell code |
| Wallpaper | `jarabe.desktop.homebackgroundbox.HomeBackgroundBox` | GSettings, GdkPixbuf scaling, Cairo paint; not GTK CSS | live GSettings signal |
| Icon rendering | `sugar3.graphics.icon` | SVG entity substitution, Cairo/Rsvg, `XoColor` fill/stroke | shell/Activity restart |
| Activity color/state | `ActivityIcon`, `CurrentActivityIcon`, shell Activity model, `XoColor` | bundle/Journal/profile color semantics | intentional; do not normalize |

## Commands

### Runtime information

```sh
make sugar-info
```

Reports versions, PIDs, process relationships, X11/Home, session D-Bus,
`PYTHONPATH`, module paths, active Sugar theme, font, and package ownership.
This is the first command to run when debugging.

### Edit, deploy, and reload

```sh
$EDITOR sugar-overlay/src/jarabe/desktop/viewtoolbar.py
# Increment archiso/.../usr/share/aspartame/ui-version for a visible revision.
make sugar-reload
```

The reload command:

1. reports git/UI revisions;
2. compiles every overlay file in memory for syntax;
3. verifies generated patches against the official package archive;
4. checks VM SSH and exact guest Sugar package version;
5. synchronizes changed files and Aspartame diagnostics;
6. compares source/runtime SHA-256 manifests;
7. records old PIDs;
8. terminates the correct `aspartame` shell PID;
9. waits for a new shell;
10. checks Metacity, `org.laptop.Shell`, Home X window, imports, and fatal logs;
11. prints new PIDs and saves a report under `reports/reloads/`.

Host `sudo` is used only to write the QEMU 9p runtime directory, which is
root-owned because of the current `security_model=none` development mount. It
does not install host packages or alter the host desktop.

### Full graphical-session restart

```sh
make sugar-session-restart
```

Use this only for session/X changes or recovery. The command proves that Xorg
and Sugar PIDs changed and runs the same health checks afterward.

### Logs

```sh
make sugar-logs
LINES=50 make sugar-logs
./scripts/sugar-logs.sh --lines 50
```

The command includes the current Sugar shell, datastore, development marker,
serious-signature summary, and user-session journal. Current observed
`g_value_type_compatible`/`buddy` warnings are displayed, not suppressed; their
root cause is not yet isolated.

Primary Sugar logs are:

```text
/home/aspartame/.sugar/default/logs/shell.log
/home/aspartame/.sugar/default/logs/datastore.log
/home/aspartame/.sugar/default/logs/<old-session>/shell.log
```

### Screenshot and visual proof

```sh
make sugar-screenshot
```

The host asks XRandR for the active guest resolution, captures `DISPLAY=:0`
inside the guest with ffmpeg, copies the PNG over localhost-only SSH, and prints
its dimensions and SHA-256. Files go to `reports/screenshots/` and are ignored
by git. This does not invoke the host screenshot UI or alter host hotkeys.

For a visual change, record:

```text
[ ] source file and UI revision changed
[ ] make sugar-patch-check passed
[ ] make sugar-reload passed
[ ] expected module path points into /mnt/aspartame-dev/sugar/src
[ ] no new fatal shell-log signature
[ ] screenshot/direct observation shows the requested object and geometry
```

## QEMU and SSH

Start the existing development VM with:

```sh
make run
```

QEMU forwards only host `127.0.0.1:2222` to guest SSH port 22 and exports the
host runtime directory as the `aspartame-dev` 9p mount. Open a shell with:

```sh
./scripts/ssh-asp
```

The helper uses an OpenSSH control socket so a command sequence does not ask for
the SSH password repeatedly. It does not expose SSH to the LAN.

## Recovery

If a bad overlay prevents Sugar from starting:

```sh
./scripts/ssh-asp
/usr/local/bin/aspartame-sugar-logs --lines 200
```

To prove the packaged fallback, recoverably move only the generated runtime
source aside, then restart the graphical session:

```sh
mv /mnt/aspartame-dev/sugar/src /mnt/aspartame-dev/sugar/src.disabled
systemctl restart getty@tty1.service
```

Restore it with:

```sh
mv /mnt/aspartame-dev/sugar/src.disabled /mnt/aspartame-dev/sugar/src
```

Do not edit `/usr/lib/python*/site-packages` to recover. Fix the repository
source and redeploy. The runtime tree can be regenerated; the repository
source and persistent `/home/aspartame` are the important state.

## Confirmed traps

- **Edited the wrong copy.** The package under `/usr/lib` and the 9p package
  both exist. `make sugar-info` identifies the active one.
- **Partial Python package overlay did nothing.** A loose nested module did not
  override the regular packaged `jarabe`; the complete package root is needed.
- **Restart helper targeted root.** The old helper trusted `$USER`; over root
  SSH it found no shell. The repository-owned helper explicitly targets
  `aspartame`.
- **A “shell” restart also changed D-Bus and Metacity.** This follows from the
  current `dbus-run-session` supervisor boundary and is now reported.
- **Persistent `.xinitrc` hid ISO changes.** `.xinitrc` is now a stable launcher
  for the system-owned `aspartame-x-session`, with a one-time backup migration.
- **GSettings said Adwaita while Sugar visibly used another theme.**
  `jarabe.main` sets `sugar-72` process-locally after startup.
- **Nested import probes had side effects.** Diagnostics now resolve files from
  the selected package root without importing Frame/Journal modules.
- **Host screenshot tools interfered with host shortcuts.** Visual capture now
  occurs entirely in guest X11 and transfers over SSH.
- **Source edits alone were treated as proof.** Reload now requires hashes,
  runtime paths, health checks, logs, and visual evidence.
