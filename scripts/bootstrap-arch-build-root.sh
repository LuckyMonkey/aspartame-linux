#!/usr/bin/env bash
set -euo pipefail

build_root=${ASPARTAME_BUILD_ROOT:-/media/freezer/SteamLibrary/vms/aspartame-build/root.x86_64}
project_root=${ASPARTAME_PROJECT_ROOT:-/home/freezer/Projects/aspartame}
mount_point="$build_root/mnt/aspartame"

test -x "$build_root/bin/arch-chroot" || {
    echo "missing Arch bootstrap root: $build_root" >&2
    exit 2
}
test -f "$project_root/Makefile" || {
    echo "missing Aspartame repository: $project_root" >&2
    exit 2
}

mkdir -p "$mount_point"
mount --bind "$project_root" "$mount_point"
cleanup() { umount "$mount_point" 2>/dev/null || true; }
trap cleanup EXIT

mirror="$build_root/etc/pacman.d/mirrorlist"
sed -i 's|^#Server = https://geo.mirror.pkgbuild.com/|Server = https://geo.mirror.pkgbuild.com/|' "$mirror"

"$build_root/bin/arch-chroot" "$build_root" /bin/bash -lc '
    set -euo pipefail
    pacman-key --init
    pacman-key --populate archlinux
    pacman -Sy --noconfirm --needed archiso git
'

