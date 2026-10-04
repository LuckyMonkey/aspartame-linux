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
# The preview's generated Python config records the development prefix. Rewrite
# that prefix in staged Python sources so Frame/extensions and control-panel
# discovery stay inside the standalone image.
while IFS= read -r -d '' source_file; do
    sed -i 's#/home/aspartame/Development/gtk4-preview#/usr/lib/aspartame/gtk4-preview#g' \
        "$source_file"
done < <(find "$preview_root/gtk4-preview/sources" -type f -name '*.py' -print0)
# Stage the built GTK4 upstream Activities from the archive, not their GTK3
# reference copies in packages/upstream-activities. Refresh checked-in native
# bundles even when an older preview left a real bundle directory: ln -sfn
# into that directory only created an unused nested link.
activities="$preview_root/gtk4-preview/prefix/share/sugar/activities"
for activity in Log ImageViewer Help Count Calculate Finance Clock JAMClock \
               Mastermind Poll Mancala Reversi Jumble NumberRush AcrossDown IQ \
               AppelHaken BallAndBrick Implode PlayGo BlockParty TypingTurtle \
               Memorize Maze FotoToon Portfolio Markdown Words LastOneLoses \
               GetThingsDone Gridpaint Stopwatch Gears TurtleArt GameOfLife \
               ColorMyWorld Abacus Planets Write ConnectTheDots Pippy Paint \
               DiamondFusion Level Moon GetBooks Jukebox Read Browse; do
    target="$activities/$activity.activity"
    case "$activity" in
        Log) source="$preview_root/gtk4-preview/sources/log-activity" ;;
        ImageViewer) source="$preview_root/gtk4-preview/sources/imageviewer-activity" ;;
        Help) source="$project_root/packages/gtk4-help-activity" ;;
        Count) source="$project_root/packages/gtk4-count-activity" ;;
        Calculate) source="$project_root/packages/gtk4-calculate-activity" ;;
        Finance) source="$project_root/packages/gtk4-finance-activity" ;;
        Clock) source="$project_root/packages/gtk4-clock-activity" ;;
        JAMClock) source="$project_root/packages/gtk4-jamclock-activity" ;;
        Mastermind) source="$project_root/packages/gtk4-mastermind-activity" ;;
        Poll) source="$project_root/packages/gtk4-poll-activity" ;;
        Mancala) source="$project_root/packages/gtk4-mancala-activity" ;;
        Reversi) source="$project_root/packages/gtk4-reversi-activity" ;;
        Jumble) source="$project_root/packages/gtk4-jumble-activity" ;;
        NumberRush) source="$project_root/packages/gtk4-numberrush-activity" ;;
        AcrossDown) source="$project_root/packages/gtk4-acrossdown-activity" ;;
        IQ) source="$project_root/packages/gtk4-iq-activity" ;;
        AppelHaken) source="$project_root/packages/gtk4-appelhaken-activity" ;;
        BallAndBrick) source="$project_root/packages/gtk4-ballandbrick-activity" ;;
        Implode) source="$project_root/packages/gtk4-implode-activity" ;;
        PlayGo) source="$project_root/packages/gtk4-playgo-activity" ;;
        BlockParty) source="$project_root/packages/gtk4-blockparty-activity" ;;
        TypingTurtle) source="$project_root/packages/gtk4-typingturtle-activity" ;;
        Memorize) source="$project_root/packages/gtk4-memorize-activity" ;;
        Maze) source="$project_root/packages/gtk4-maze-activity" ;;
        FotoToon) source="$project_root/packages/gtk4-fototoon-activity" ;;
        Portfolio) source="$project_root/packages/gtk4-portfolio-activity" ;;
        Markdown) source="$project_root/packages/gtk4-markdown-activity" ;;
        Words) source="$project_root/packages/gtk4-words-activity" ;;
        LastOneLoses) source="$project_root/packages/gtk4-last-one-loses-activity" ;;
        GetThingsDone) source="$project_root/packages/gtk4-gtd-activity" ;;
        Gridpaint) source="$project_root/packages/gtk4-gridpaint-activity" ;;
        Stopwatch) source="$project_root/packages/gtk4-stopwatch-activity" ;;
        Gears) source="$project_root/packages/gtk4-gears-activity" ;;
        TurtleArt) source="$project_root/packages/gtk4-turtleart-activity" ;;
        GameOfLife) source="$project_root/packages/gtk4-gameoflife-activity" ;;
        ColorMyWorld) source="$project_root/packages/gtk4-colormyworld-activity" ;;
        Abacus) source="$project_root/packages/gtk4-abacus-activity" ;;
        ConnectTheDots) source="$project_root/packages/gtk4-connect-the-dots-activity" ;;
        Moon) source="$project_root/packages/gtk4-moon-activity" ;;
        Planets) source="$project_root/packages/gtk4-planets-activity" ;;
        Paint) source="$project_root/packages/gtk4-paint-activity" ;;
        Pippy) source="$project_root/packages/gtk4-pippy-activity" ;;
        Write) source="$project_root/packages/gtk4-write-activity" ;;
        Jukebox) source="$project_root/packages/gtk4-jukebox-activity" ;;
        DiamondFusion) source="$project_root/packages/gtk4-diamond-fusion-activity" ;;
        Level) source="$project_root/packages/gtk4-level-activity" ;;
        GetBooks) source="$project_root/packages/gtk4-get-books-activity" ;;
        Read) source="$project_root/packages/gtk4-read-activity" ;;
        Browse) source="$project_root/packages/gtk4-browse-activity" ;;
    esac
    test -f "$source/activity/activity.info" || {
        echo "missing standalone GTK4 $activity source: $source" >&2
        exit 2
    }
    # The standalone archive may contain an Activity directory with an old
    # top-level entrypoint plus a development symlink. Clear its contents and
    # copy the checked-in package into the Activity root; copying the source
    # directory itself into an existing target would leave the stale entrypoint
    # in place and create an unused nested package directory.
    rm -rf -- "$target"
    mkdir -p -- "$target"
    find "$target" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
    cp -a "$source/." "$target/"
done
# Resolve the remaining development-only Activity links by package basename.
# This covers the catalog without hard-coding every bundle name.
while IFS= read -r -d '' link; do
    target=$(readlink "$link")
    package=$(basename "$target")
    source="$project_root/packages/$package"
    test -e "$source" || continue
    rm -f "$link"
    cp -a "$source" "$link"
done < <(find "$activities" -type l -print0)
install -d "$preview_root/gtk4-preview/gtk4-overlay/src" \
          "$preview_root/gtk4-preview/scripts"
cp -a "$project_root/gtk4-overlay/." \
      "$preview_root/gtk4-preview/gtk4-overlay/"
install -D -m 0755 "$project_root/scripts/snakepit.py" \
    "$profile_stage/airootfs/usr/share/aspartame/snakepit.py"
for helper in sugar-gtk4-run.sh sugar-gtk4-session.sh sugar-gtk4-space.sh \
             sugar-chirality-space.sh \
             sugar-chirality-activity.py \
             sugar-gtk4-chirality-activity-roundtrip.py \
             sugar-gtk4-chirality-object-roundtrip.py \
             sugar-gtk4-chirality-crash-roundtrip.py \
             sugar-gtk4-chirality-resume-roundtrip.py \
             sugar-gtk4-share-join-roundtrip.py \
             sugar-gtk4-pippy-runtime-probe.py \
             aspartame_chirality.py sugar-chirality.py \
             sugar-gtk4-runtime-check.sh sugar-gtk4-lifecycle-probe.sh \
             sugar-gtk3-lifecycle-probe.sh \
             sugar-gtk4-spaces-menu-probe.py sugar-gtk4-side-by-side-probe.sh \
             sugar-gtk4-visual-sweep-guest.sh \
             sugar-gtk4-activity-matrix.sh \
             sugar-x11-workspace.py; do
    install -m 0755 "$project_root/scripts/$helper" \
        "$preview_root/gtk4-preview/scripts/$helper"
done
printf 'standalone-preview=%s\n' "$(sha256sum "$preview_archive" | awk '{print $1}')" \
    > "$preview_root/gtk4-preview/STANDALONE-MANIFEST"

mkarchiso -v -w "$WORK_DIR" -o "$OUT_DIR" "$profile_stage"
