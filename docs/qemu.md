# QEMU reference machine

```sh
make iso
RAM=4096 CPUS=4 make run
```

The runner uses KVM and `-cpu host` when `/dev/kvm` is accessible, otherwise it
falls back to TCG. It provides a q35 machine, virtio disk/network, virtio VGA,
USB tablet, PulseAudio/PipeWire-backed AC97 audio, and a separate persistent
qcow2 test disk at `runtime/`.

The virtual display advertises 1920x1080 through virtio-vga. The runner uses
the blank `runtime/aspartame-test.qcow2` for the live system and a separate
`runtime/aspartame-data.qcow2` for persistent `/home/aspartame` data. The data
disk is formatted on first boot only when empty.

The runner also exports `runtime/aspartame-dev/` as the `aspartame-dev` 9p
share. It is mounted automatically before the graphical session at
`/mnt/aspartame-dev`. Host-edited Sugar Python sources placed under
`runtime/aspartame-dev/sugar/src/` override the packaged shell.

`aspartame-restart-sugar` terminates only the Sugar shell. The `.xinitrc`
session loop starts it again, so Sugar changes can be tested without rebooting
QEMU or the guest OS. Packaged Sugar remains the fallback when the source
overlay is absent.

Sugar's native frame remains hidden during normal use. Press `F6` to reveal it,
or move the pointer into a screen corner/edge. Selecting Home, Group,
Neighborhood, Activity, or Journal performs the action and returns to the
normal hidden-frame state. The clock is centered within the native navigation
toolbar.

SSH control is available only through localhost port 2222:

```sh
./scripts/ssh-asp
./scripts/ssh-asp /usr/local/bin/aspartame-restart-sugar
```

The test image is configured for root SSH using the development password, and
the control path is verified. QEMU forwards only `127.0.0.1:2222` to the guest,
so the SSH service is not exposed to the LAN. The direct guest SSH helper is
started after NetworkManager comes up; the service also remains enabled for
normal systemd startup.

The guest-side SSH service is intentionally limited to this VM and localhost
forwarding. It is development access, not an installation security model.

## Persistence contract

The second QEMU disk, `runtime/aspartame-data.qcow2`, is the persistent home
volume. On every boot the guest waits for `/dev/vdb`, formats it only when it
has no filesystem, mounts it at `/home/aspartame`, and verifies that the mount
source is exactly `/dev/vdb` before starting X/Sugar. If that check fails,
Sugar does not start, preventing a session from silently writing profile,
Journal, dconf, or layout changes to the disposable live root.

Sugar profile color, Home/Group/Neighborhood layout choices, Journal data,
activity history, browser profile data, and user configuration under
`/home/aspartame` therefore survive Sugar restarts and QEMU relaunches. The
host launch command must continue using the same `DATA_DISK`; replacing it
intentionally creates a new user state.
