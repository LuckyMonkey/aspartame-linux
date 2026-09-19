#!/usr/bin/env bash
set -euo pipefail

# Build Aspartame's one rebuilt system package, sugar-toolkit-gtk3, and publish
# it into the local repository the archiso profile installs from.
#
# This exists for a single delta: the key grabber has to release its X11
# passive grabs, or the classic Space keeps F1-F8 and no function key reaches
# the modern Space. Everything else about the package is Arch's.
#
# Deliberately not a generic package framework: one package, one patch.

project_root=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
pkgdir="$project_root/packages/sugar-toolkit-gtk3"
patch="$project_root/patches/system/0001-sugar-toolkit-gtk3-keygrabber-release.patch"
repo_dir=${ASPARTAME_PKG_REPO:-/mnt/aspartame-artifacts/repo}
build_dir=${ASPARTAME_PKG_BUILD:-${TMPDIR:-/tmp}/aspartame-pkgbuild}

test -f "$pkgdir/PKGBUILD" || { echo "missing PKGBUILD: $pkgdir" >&2; exit 2; }
test -f "$patch" || { echo "missing carried patch: $patch" >&2; exit 2; }
command -v makepkg >/dev/null || { echo 'makepkg is required' >&2; exit 2; }

# makepkg refuses to run as root, and the build root enters as root.
if [ "$(id -u)" -eq 0 ]; then
    builder=${ASPARTAME_PKG_USER:-builder}
    id "$builder" >/dev/null 2>&1 || useradd -m "$builder"
    install -d -o "$builder" -g "$builder" "$build_dir" "$repo_dir"
    cp -a "$pkgdir/." "$build_dir/"
    cp -a "$patch" "$build_dir/"
    chown -R "$builder:$builder" "$build_dir"
    exec runuser -u "$builder" -- env ASPARTAME_PKG_REPO="$repo_dir" \
        ASPARTAME_PKG_BUILD="$build_dir" ASPARTAME_PKG_PREPARED=1 \
        "${BASH_SOURCE[0]}" "$@"
fi

if [ "${ASPARTAME_PKG_PREPARED:-0}" != 1 ]; then
    mkdir -p "$build_dir" "$repo_dir"
    cp -a "$pkgdir/." "$build_dir/"
    cp -a "$patch" "$build_dir/"
fi

cd "$build_dir"
# The ArchISO build installs the profile dependencies before this helper runs.
# Avoid makepkg's interactive dependency installer: the isolated builder user
# has no password-bearing sudo/su session in the chroot.
makepkg --force --nodeps --noconfirm

built=$(ls -1t "$build_dir"/*.pkg.tar.* 2>/dev/null | head -1)
test -n "$built" || { echo 'makepkg produced no package' >&2; exit 1; }

mkdir -p "$repo_dir"
cp -f "$built" "$repo_dir/"
repo-add --quiet "$repo_dir/aspartame.db.tar.gz" "$repo_dir/$(basename "$built")"

printf 'built: %s\n' "$(basename "$built")"
printf 'repository: %s\n' "$repo_dir"
