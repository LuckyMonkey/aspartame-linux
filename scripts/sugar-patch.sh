#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source "$project_root/sugar-overlay/UPSTREAM"
files_list="$project_root/sugar-overlay/files.list"
overlay_root="$project_root/sugar-overlay/src"
build_root=${BUILD_ROOT:-/media/freezer/SteamLibrary/vms/aspartame-build}
archive=${SUGAR_PACKAGE_ARCHIVE:-$build_root/root.x86_64/var/cache/pacman/pkg/$SUGAR_ARCHIVE}
mode=${1:-check}

test -f "$archive" || { echo "missing official package archive: $archive" >&2; exit 2; }
actual_hash=$(sha256sum "$archive" | awk '{print $1}')
test "$actual_hash" = "$SUGAR_ARCHIVE_SHA256" || {
    echo "Sugar package hash mismatch: $actual_hash" >&2
    exit 3
}

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT
bsdtar -xf "$archive" -C "$tmp_dir"
site_packages=$(find "$tmp_dir/usr/lib" -type d -path '*/site-packages' -print -quit)
test -n "$site_packages" || { echo 'site-packages missing from Sugar archive' >&2; exit 4; }
generated="$tmp_dir/0001-integrated-navigation.patch"

while IFS= read -r relative; do
    test -n "$relative" || continue
    test -f "$site_packages/$relative" || { echo "base file missing: $relative" >&2; exit 5; }
    test -f "$overlay_root/$relative" || { echo "overlay file missing: $relative" >&2; exit 6; }
    diff -u --label "$relative" --label "$relative" \
        "$site_packages/$relative" "$overlay_root/$relative" >> "$generated" ||
        test $? -eq 1
done < "$files_list"

case "$mode" in
    check)
        cmp "$generated" "$project_root/patches/sugar/0001-integrated-navigation.patch"
        cmp "$generated" "$project_root/archiso/aspartame/airootfs/usr/share/aspartame/0001-integrated-navigation.patch"
        echo "Sugar overlay/patch sync: PASS ($SUGAR_PACKAGE $SUGAR_VERSION)"
        ;;
    update)
        install -m 0644 "$generated" "$project_root/patches/sugar/0001-integrated-navigation.patch"
        install -m 0644 "$generated" "$project_root/archiso/aspartame/airootfs/usr/share/aspartame/0001-integrated-navigation.patch"
        echo "Updated Sugar patches from $SUGAR_PACKAGE $SUGAR_VERSION"
        ;;
    *)
        echo 'usage: sugar-patch.sh [check|update]' >&2
        exit 64
        ;;
esac
