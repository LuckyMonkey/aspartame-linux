#!/usr/bin/env bash
set -euo pipefail

if test "$(id -u)" -ne 0; then
    exec sudo -- "$0" "$@"
fi

# Never create or clean build mounts in the host mount namespace.  Without
# this boundary, an interrupted cleanup can see through a bind mount and
# detach host mounts such as /sys/fs/cgroup or /run/user.
if test "${ASPARTAME_MOUNT_NAMESPACE:-0}" != 1; then
    export ASPARTAME_MOUNT_NAMESPACE=1
    exec unshare --mount --propagation private "$0" "$@"
fi

build_area=${BUILD_ROOT:-/media/freezer/SteamLibrary/vms/aspartame-build}
build_root=${ARCH_ROOT:-$build_area/root.x86_64}
project_root=${PROJECT_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}
artifact_root=${ARTIFACT_ROOT:-$build_area/artifacts}
root_mount=$build_root/mnt/aspartame
artifact_mount=$build_root/mnt/aspartame-artifacts
resolver_mount=$build_root/etc/resolv.conf

test -x "$build_root/bin/arch-chroot" || {
    echo "error: Arch build root is missing: $build_root" >&2
    echo "run scripts/bootstrap-arch-build-root.sh first" >&2
    exit 2
}
test -f "$project_root/archiso/aspartame/profiledef.sh" || {
    echo "error: invalid Aspartame project root: $project_root" >&2
    exit 2
}

mkdir -p "$root_mount" "$artifact_root" "$artifact_mount"
mount --bind "$build_root" "$build_root"
mount --bind "$project_root" "$root_mount"
mount --bind "$artifact_root" "$artifact_mount"
mount --bind /etc/resolv.conf "$resolver_mount"
mount -t proc proc "$build_root/proc"
mount --bind /sys "$build_root/sys"
mount --make-rslave "$build_root/sys"
mount --bind /dev "$build_root/dev"
mount --make-rslave "$build_root/dev"
# The build only needs a private runtime directory; binding the host's /run
# recursively leaks desktop mounts (GVFS, portals, snap namespaces) into the
# chroot and makes cleanup unnecessarily fragile.
mount -t tmpfs -o mode=755,nosuid,nodev tmpfs "$build_root/run"
detach_tree() {
    local base=$1 targets
    for _ in $(seq 1 12); do
        targets=$(findmnt --list --submounts -n -o TARGET 2>/dev/null |
            awk -v base="$base" 'index($0, base) == 1 && (length($0) == length(base) || substr($0, length(base) + 1, 1) == "/")' |
            sort -r -u || true)
        test -n "$targets" || return 0
        while IFS= read -r target; do
            umount -l "$target" 2>/dev/null || true
        done <<< "$targets"
    done
}
cleanup() {
    detach_tree "$build_root/run"
    detach_tree "$build_root/dev"
    detach_tree "$build_root/sys"
    detach_tree "$build_root/proc"
    detach_tree "$artifact_mount"
    detach_tree "$root_mount"
    detach_tree "$resolver_mount"
    detach_tree "$build_root"
}
trap cleanup EXIT

chroot "$build_root" /bin/bash -lc '
    set -euo pipefail
    PROFILE=/mnt/aspartame/archiso/aspartame \
    OUT_DIR=/mnt/aspartame-artifacts/out \
    WORK_DIR=/mnt/aspartame-artifacts/work \
    /mnt/aspartame/scripts/build-iso.sh
'
