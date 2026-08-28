#!/usr/bin/env bash
set -euo pipefail

if test "$(id -u)" -ne 0; then
    exec sudo -- "$0" "$@"
fi

build_area=${BUILD_ROOT:-/media/freezer/SteamLibrary/vms/aspartame-build}
build_root=${ARCH_ROOT:-$build_area/root.x86_64}
project_root=${PROJECT_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}
artifact_root=${ARTIFACT_ROOT:-$build_area/artifacts}
root_mount=$build_root/mnt/aspartame
artifact_mount=$build_root/mnt/aspartame-artifacts

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
mount -t proc proc "$build_root/proc"
mount --rbind /sys "$build_root/sys"
mount --make-rslave "$build_root/sys"
mount --rbind /dev "$build_root/dev"
mount --make-rslave "$build_root/dev"
mount --rbind /run "$build_root/run"
mount --make-rslave "$build_root/run"
detach_tree() {
    local base=$1 targets
    for _ in $(seq 1 12); do
        targets=$(findmnt -R -n -o TARGET "$base" 2>/dev/null | sort -r || true)
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
