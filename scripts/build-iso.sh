#!/usr/bin/env bash
set -euo pipefail

: "${PROFILE:?PROFILE is required}"
: "${OUT_DIR:?OUT_DIR is required}"
: "${WORK_DIR:?WORK_DIR is required}"

if ! command -v mkarchiso >/dev/null 2>&1; then
    echo "error: mkarchiso is required; run this from an Arch build environment" >&2
    exit 2
fi

mkdir -p "$OUT_DIR" "$WORK_DIR"
rm -rf -- "$WORK_DIR"
mkdir -p "$WORK_DIR"

# The GTK4 preview is a built runtime, not a development-only 9p mount. The
# archive is produced from the pinned guest build and staged into a temporary
# profile so the checked-in ArchISO profile remains small and reviewable.
preview_archive=${GTK4_PREVIEW_ARCHIVE:-$(dirname "$OUT_DIR")/gtk4-preview-standalone.tar.gz}
test -f "$preview_archive" || {
    echo "missing standalone GTK4 runtime archive: $preview_archive" >&2
    echo 'Create it from the pinned guest preview, then rerun the ISO build.' >&2
    exit 2
}
profile_stage="$WORK_DIR/profile"
# PROFILE points at <project>/archiso/aspartame.  The project root is one
# level above the profile's parent (not two levels, which would resolve to the
# chroot's /mnt directory when invoked by build-in-arch-root.sh).
project_root=$(CDPATH= cd -- "$(dirname "$PROFILE")/.." && pwd)
mkdir -p "$profile_stage"
cp -a "$PROFILE/." "$profile_stage/"
preview_root="$profile_stage/airootfs/usr/lib/aspartame"
mkdir -p "$preview_root"
tar -xzf "$preview_archive" -C "$preview_root"
test -x "$preview_root/gtk4-preview/venv/bin/python" || {
    echo 'standalone GTK4 archive is missing venv/bin/python' >&2
    exit 2
}
# The guest prefix contains development symlinks for these two shell-owned
# Activities. Resolve them from the repository while staging the image so no
# `/home/aspartame` or `/mnt/aspartame-dev` path leaks into the ISO.
activities="$preview_root/gtk4-preview/prefix/share/sugar/activities"
for activity in Log Help; do
    target="$activities/$activity.activity"
    if test -L "$target"; then
        rm -f "$target"
        case "$activity" in
            Log) cp -a "$project_root/packages/upstream-activities/log-activity" "$target" ;;
            Help) cp -a "$project_root/packages/gtk4-help-activity/." "$target" ;;
        esac
    fi
done
# ImageViewer is pinned in the preview source tree rather than a repository
# package; resolve that guest-home link into the staged prefix as well.
imageviewer="$activities/ImageViewer.activity"
if test -L "$imageviewer" && test -d "$preview_root/gtk4-preview/sources/imageviewer-activity"; then
    rm -f "$imageviewer"
    cp -a "$preview_root/gtk4-preview/sources/imageviewer-activity" "$imageviewer"
fi
# Resolve the remaining development-only Activity links by package basename.
# This covers the catalog without hard-coding every bundle name and also
# handles nested executable links such as Count.activity/gtk4-count-activity.
while IFS= read -r -d '' link; do
    target=$(readlink "$link")
    package=$(basename "$target")
    source="$project_root/packages/$package"
    test -e "$source" || continue
    rm -f "$link"
    if test -d "$source"; then
        cp -a "$source" "$link"
    else
        cp -a "$source" "$link"
    fi
done < <(find "$activities" -type l -print0)
install -d "$preview_root/gtk4-preview/gtk4-overlay/src" \
          "$preview_root/gtk4-preview/scripts"
cp -a "$project_root/gtk4-overlay/." \
      "$preview_root/gtk4-preview/gtk4-overlay/"
for helper in sugar-gtk4-run.sh sugar-gtk4-session.sh sugar-gtk4-space.sh \
             sugar-x11-workspace.py; do
    install -m 0755 "$project_root/scripts/$helper" \
        "$preview_root/gtk4-preview/scripts/$helper"
done
printf 'standalone-preview=%s\n' "$(sha256sum "$preview_archive" | awk '{print $1}')" \
    > "$preview_root/gtk4-preview/STANDALONE-MANIFEST"

mkarchiso -v -w "$WORK_DIR" -o "$OUT_DIR" "$profile_stage"
