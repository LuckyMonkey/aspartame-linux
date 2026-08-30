# Aspartame persistence

The current QEMU development image has two different persistence layers:

- `aspartame-data.qcow2` (`/dev/vdb`) is an ext4 filesystem mounted at
  `/home/aspartame`. Journal data, Sugar preferences, Activity ratings, and
  ordinary user files survive VM restarts.
- The operating-system root currently comes from the read-only archiso
  squashfs. Its writable live overlay is temporary. Packages installed while
  testing, such as `noto-fonts-emoji`, must therefore also be added to
  `packages.x86_64` and included in a rebuilt ISO.

This is deliberate for the live-image bootstrap, but it is not full system
persistence. A future persistent-system mode must use the blank 32 GiB
`aspartame-test.qcow2` as an installed root filesystem, or use a verified
archiso persistent overlay. That transition must be explicit because it
changes the boot model and may format the selected system disk.

The supported current workflow is:

```bash
make iso
sudo -A make run
```

Do not install packages with signature verification disabled. The test VM's
pacman keyring and official mirror must be initialized before live package
installation.
