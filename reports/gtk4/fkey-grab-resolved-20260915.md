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

## Packaging note

The guest now runs a rebuilt `/usr/lib/libsugarext.so` that is not the one
pacman installed. A package rebuild carrying this patch is required for the
ISO; until then a fresh image will still show the old behaviour.
