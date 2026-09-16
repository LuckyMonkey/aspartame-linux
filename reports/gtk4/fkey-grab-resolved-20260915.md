# F-key delivery to the modern Space — resolved — 2026-09-15

Closes the frontier recorded in `fkey-grab-frontier-20260915.md`, which
merged W6 (F7/F8 Space switching) and W7 (Frame navigation): no function key
reached the GTK4 shell while the classic GTK3 shell was running, although
ordinary keys did.

## Root cause, in the C

`SugarKeyGrabber` (sugar-toolkit-gtk3 v0.121, Arch `sugar-toolkit-gtk3
0.121-7`, `/usr/lib/libsugarext.so`) only ever *took* X11 passive grabs:

- `sugar_key_grabber_grab_keys()` grabbed each key in the new list and
  appended it to `grabber->keys`, never ungrabbing the previous set. Grabs
  were cumulative, and an empty list was a no-op, so a caller could not hand
  a key back.
- `dispose()` freed the key list without ungrabbing, and left the GDK event
  filter installed with the freed object as its data, so events kept being
  dispatched against freed memory once the grabber went away
  (`instance of invalid non-instantiatable type 'void'` in the classic log).

The classic shell's `_sync_space_grab()` did the right thing at the Python
level — call `grab_keys([])` when the modern Space is selected, and log
`Spaces key ownership: GTK3 released (workspace=1)` — but the release was a
no-op in the library, so F1-F8 stayed owned for the life of the process.

## Fix

`patches/system/0001-sugar-toolkit-gtk3-keygrabber-release.patch`:
`grab_keys()` ungrabs and frees the previous set before taking the new one,
and `dispose()` ungrabs, detaches the event filter, and chains up.

Built from a v0.121 checkout and installed over the packaged library; the
original is backed up at `/root/aspartame-libsugarext-backup-20260915/`.

## Evidence

Grabs, with the modern Space selected (`sugar-x11-keygrab-probe.py`):

| | before | after |
|---|---|---|
| F1-F8 | HELD by another client | free |
| Tab, a | free | free |

Modern Space, physical keys, each producing a distinct captured view:

| Key | Result |
|---|---|
| F3 | Home |
| F1 | Neighborhood |
| F5 | Journal |
| F6 | Frame revealed — all four panels: zoom toolbar, Journal and Help, the XO owner icon, and the device tray |
| Escape | Frame dismissed, back to Home |

Physical Space switching, two consecutive round trips:

    F7 -> runtime-check=ok target=gtk3 pid=58951 desktop=0
    F8 -> runtime-check=ok target=gtk4 pid=51180 desktop=1
    F7 -> runtime-check=ok target=gtk3 pid=58951 desktop=0
    F8 -> runtime-check=ok target=gtk4 pid=51180 desktop=1

The classic shell's dangling-filter warnings are gone (0 occurrences since
the restart), and the Activity keyboard path still passes: a Help Activity
launched with no pointer interaction accepted `Yo` with correct
capitalisation.

## Packaging

The fix ships as a rebuilt Arch package, not a hand-installed library:

- `packages/sugar-toolkit-gtk3/PKGBUILD` is Arch's recipe for
  extra/sugar-toolkit-gtk3 0.121-7 plus the carried patch, at `pkgrel=7.1` so
  pacman prefers it. Its `pkgdesc` names the delta.
- `scripts/build-sugar-toolkit-package.sh` builds that one package and
  publishes it to a local repository.
- `archiso/aspartame/pacman.conf` adds that repository ahead of `[extra]`, and
  `profiledef.sh` points `pacman_conf` at it so the profile carries its own
  configuration.
- `scripts/build-in-arch-root.sh` builds the package before `mkarchiso` runs.

Arch's recipe has to be followed exactly, not approximated. A first attempt
that used `autogen.sh` and default flags produced a package whose
cross-library symbols failed to resolve at load time
(`libsugarext.so.0: undefined symbol: sugar_event_controller_reset`), which
broke the classic shell outright. Arch drops `-fno-plt` and `-Wl,-z,now`
with the comment "Hardened build is not supported"; that adjustment is
required, and the three upstream `sed` fixes are carried too.

Verified by installing the built package over the stock one:

    pacman -Qo /usr/lib/libsugarext.so.0.0.0
      -> owned by sugar-toolkit-gtk3 0.121-7.1

with an A/B either side of it: the stock library reported F1/F6/F7 `HELD by
another client`, the packaged rebuild reports F1-F8 `free` while the classic
shell stays alive (pid 90516), the classic session reports healthy on every
check, F1/F3/F5/F6 and Escape all work, physical F7->F8 round-trips twice,
and a Help Activity launched without pointer interaction accepts `Ab`.

## Still to prove on the next ISO build

`mkarchiso` consuming the package from the profile's `[aspartame]` repository
has not been executed. The host's SteamLibrary volume is not mounted, so the
build root, VM disks and artifacts all sit on `/` with 3.9 GB free, and a full
image build is not safe to start there. The package path itself is proven up
to and including installation; what remains is one ISO build once that volume
is back.
