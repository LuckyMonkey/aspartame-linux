# Aspartame

**Sugar on Arch.**

Aspartame is an Arch-based desktop distribution with Sugar as its primary
desktop. The bootstrap target is a reproducible archiso live image that boots
to a usable Sugar session in QEMU, with networking, Firefox, terminal,
storage, sound infrastructure, and printing.

## Quick start

The build uses an official Arch bootstrap root on SteamLibrary. This keeps
archiso's package cache and large work/output trees off the Ubuntu root
filesystem.

```sh
git clone https://github.com/LuckyMonkey/aspartame-linux.git
cd aspartame-linux
make iso
make run
```

The first `make iso` asks for sudo to enter the isolated Arch build root.
Run `make test` for host-side checks without building.

Use `RAM=8192 CPUS=4 make run` to override QEMU defaults. See [docs/building.md](docs/building.md) and [docs/qemu.md](docs/qemu.md).

Aspartame keeps Arch, pacman, systemd, ordinary filesystem paths, and a real
terminal beneath Sugar. Python is preferred for user-layer integration, while
system Python and low-level native infrastructure remain distribution-owned.
See [docs/philosophy.md](docs/philosophy.md).

## Current status

The repository is in bootstrap profile stage. The Ubuntu development host
does not provide `mkarchiso`; the build script intentionally stops with a
clear prerequisite error. Sugar package availability is promising on current
Arch Extra, but the actual ISO boot and Activity compatibility still need to be
tested in Arch/QEMU.

Current upstream/package findings are recorded in
[docs/sugar-current-state.md](docs/sugar-current-state.md).
