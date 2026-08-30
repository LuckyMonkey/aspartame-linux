# Aspartame persistence

The QEMU development image has two deliberately separate persistence layers:

- `aspartame-data.qcow2` (`/dev/vdb`) is an ext4 filesystem mounted at
  `/home/aspartame`. Journal data, Sugar preferences, Activity ratings, and
  ordinary user files survive VM restarts.
- `aspartame-test.qcow2` (`/dev/vda`) is labeled `ASPARTAME_COW` and is used
  by Archiso as the persistent writable system overlay at
  `/run/archiso/cowspace`. Changes to the live root, including installed
  packages and `/etc` files, survive a VM restart.
- The lower operating-system layer remains the read-only Archiso squashfs on
  the ISO. Rebuilding the ISO changes that lower layer, while the CoW disk
  retains its upper-layer changes.

The boot profile enables this with:

```text
cow_device=LABEL=ASPARTAME_COW cow_directory=aspartame cow_persistent=P
```

The system disk was formatted only after it was verified blank and backed up.
The backup is:

```text
/media/freezer/SteamLibrary/vms/aspartame-build/backups/pre-persistent-20260829-231445/
```

Restore is an explicit offline operation: stop QEMU, preserve or move the
current `runtime/aspartame-test.qcow2`, then copy the backed-up qcow2 back to
that exact runtime path. Do not format the disk again unless intentionally
resetting the system overlay.

The supported current workflow is:

```bash
make iso
sudo -A make run
```

The image recipe remains authoritative for reproducible system packages:
add packages to `archiso/aspartame/packages.x86_64` and rebuild the ISO.
Packages installed interactively in the running VM persist in the CoW layer,
but are local to that VM and are not automatically reproduced in a new CoW
disk.

Do not install packages with signature verification disabled. The test VM's
pacman keyring and official mirror must be initialized before live package
installation.
