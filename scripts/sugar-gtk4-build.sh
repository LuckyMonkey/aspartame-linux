#!/usr/bin/env bash
set -euo pipefail
if ! grep -qx 'IMAGE_ID=aspartame' /etc/os-release; then
    echo 'This build is guest-only; run it inside the Aspartame development VM.' >&2
    exit 2
fi

# The image's stable-Activity bridge deliberately pins GTK3 from
# sitecustomize. Mark every preview subprocess before Python starts so GTK4
# can be selected in the isolated toolchain without weakening stable Sugar.
export ASPARTAME_GTK4_PREVIEW=1

repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export PYTHONPATH="$repo/sugar-overlay/src${PYTHONPATH:+:$PYTHONPATH}"

root=${GTK4_ROOT:-/home/aspartame/Development/gtk4-preview}
shell="$root/sources/sugar"
toolkit="$root/sources/sugar-toolkit-gtk4"
ext="$root/sources/sugar-ext"
datastore="$root/sources/sugar-datastore"
casilda="$root/sources/casilda"
log_activity="$root/sources/log-activity"
imageviewer_activity="$root/sources/imageviewer-activity"
terminal_activity="$root/sources/terminal-activity"
native_terminal_activity="$repo/packages/gtk4-terminal-activity"
browse_activity="$root/sources/browse-activity"
native_browse_activity="$repo/packages/gtk4-browse-activity"
prefix="$root/prefix"
venv="$root/venv"
log="$root/logs/gtk4-build-$(date -u +%Y%m%dT%H%M%SZ).log"
mkdir -p "$root/logs" "$root/build"; exec > >(tee "$log") 2>&1
test -d "$shell/.git" || { echo "missing shell checkout: $shell"; exit 2; }
test -d "$toolkit/.git" || { echo "missing toolkit checkout: $toolkit"; exit 2; }
test -d "$ext/.git" || { echo "missing sugar-ext checkout: $ext"; exit 2; }
test -d "$datastore/.git" || { echo "missing sugar-datastore checkout: $datastore"; exit 2; }
test -d "$casilda/.git" || { echo "missing Casilda checkout: $casilda"; exit 2; }
test -d "$log_activity/.git" || { echo "missing Log Activity checkout: $log_activity"; exit 2; }
test -f "$log_activity/logviewer.py" || { echo "missing Log Activity source: $log_activity"; exit 2; }
test -d "$imageviewer_activity/.git" || { echo "missing Image Viewer Activity source: $imageviewer_activity"; exit 2; }
test -d "$terminal_activity/.git" || { echo "missing Terminal Activity source: $terminal_activity"; exit 2; }
test -d "$browse_activity/.git" || { echo "missing Browse Activity source: $browse_activity"; exit 2; }
if ! test -x "$venv/bin/python"; then
    python3 -m venv --system-site-packages "$venv"
fi
# Ensure preview children use the GTK3-safe runtime hook from this checkout;
# distro sitecustomize may be stale and is imported before sugar4.
venv_site=$($venv/bin/python -c 'import site; print(site.getsitepackages()[0])')
install -D -m 0644 "$repo/sugar-overlay/src/sitecustomize.py" \
    "$venv_site/sitecustomize.py"
# Expose Empy from the isolated preview venv when Arch omitted its console link.
if ! test -x "$venv/bin/empy" && test -x "$venv/bin/em.py"; then
    ln -sf "$venv/bin/em.py" "$venv/bin/empy"
fi
export PATH="$venv/bin:$PATH"
echo "toolkit: $(git -c safe.directory="$toolkit" -C "$toolkit" rev-parse HEAD)"; echo "sugar-ext: $(git -c safe.directory="$ext" -C "$ext" rev-parse HEAD)"
patch_dir=${GTK4_PATCH_DIR:-$repo/patches/gtk4-preview}
patch_state="$root/build/applied-patches"
mkdir -p "$patch_state"
# Each upstream repository carries at most a few exact patches. Sugar and the
# toolkit each carry one rebased downstream delta (0300/0301); the individual
# history lives under patches/gtk4-preview/folded/ for provenance only.
for patch in "$patch_dir"/*.patch; do
    [ -f "$patch" ] || continue
    case "$(basename "$patch")" in
        0002-*) target="$ext" ;;
        0014-*|0170-*) target="$datastore" ;;
        0029-*|0171-*) target="$log_activity" ;;
        0137-*|0138-*) target="$casilda" ;;
        0300-*) target="$shell" ;;
        0301-*) target="$toolkit" ;;
        0003-*) echo "skipping legacy Casilda 0.1 compatibility patch"; continue ;;
        *) echo "unrouted GTK4 preview patch: $patch" >&2; exit 2 ;;
    esac
    patch_name=$(basename "$patch")
    stamp="$patch_state/$patch_name.sha256"
    if (cd "$target" && patch --dry-run --reverse --force --fuzz=0 -p1 < "$patch" >/dev/null 2>&1); then
        echo "verified applied: $patch_name"
    elif (cd "$target" && patch --dry-run --forward --fuzz=0 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --forward --fuzz=0 -p1 < "$patch" >/dev/null)
        echo "applied: $patch_name"
    else
        echo "GTK4 preview patch drift: $patch_name" >&2
        echo "target: $target (run make sugar-gtk4-init to reset the pinned checkout)" >&2
        exit 2
    fi
    sha256sum "$patch" | cut -d " " -f 1 > "$stamp"
done
PYTHONPATH="$toolkit/src${PYTHONPATH:+:$PYTHONPATH}" "$venv/bin/python" -c 'import sugar4; print("sugar4: PASS", sugar4.__file__)'

python3 "$repo/scripts/repair-gtk4-controlpanel-action.py" \
    "$shell/src/jarabe/view/service.py"
install -m 0755 "$repo/scripts/sugar-activity4" "$venv/bin/sugar-activity4"
test -x "$venv/bin/sugar-activity4"

activity_dir="$prefix/share/sugar/activities"
test -f "$log_activity/activity/activity.info" || {
    echo "missing pinned Log Activity bundle: $log_activity" >&2
    exit 2
}
mkdir -p "$activity_dir"
# Previous preview builds can leave registry-generated dangling links behind.
# They make Jarabe log "No bundle" errors during startup and obscure real
# inventory failures; remove only links whose targets are already absent.
find "$activity_dir" -xtype l -delete
# A previous build may also have materialized an Activity bundle as a real
# directory.  GNU ln -sfn does not replace such a directory; it creates a
# nested symlink instead, leaving the stale top-level entrypoint authoritative.
# Clear only the known modern bundle targets before recreating their links.
activity_names=(
    Log Help Count Calculate Clock JAMClock Mastermind Poll Mancala Reversi
    Jumble NumberRush AcrossDown IQ AppelHaken BallAndBrick Implode PlayGo
    BlockParty TypingTurtle Memorize Maze FotoToon Portfolio Markdown Finance
    Words LastOneLoses GetThingsDone Gridpaint Stopwatch Gears TurtleArt
    GameOfLife ColorMyWorld Abacus Planets Write ConnectTheDots Pippy Paint
    DiamondFusion Level Moon GetBooks Jukebox Read ImageViewer Terminal Browse
)
for activity_name in "${activity_names[@]}"; do
    target="$activity_dir/${activity_name}.activity"
    if test -e "$target" && test ! -L "$target"; then
        echo "replacing stale GTK4 Activity directory: $target"
        rm -rf -- "$target"
    fi
done
ln -sfn "$log_activity" "$activity_dir/Log.activity"
help_activity="$repo/packages/gtk4-help-activity"
test -f "$help_activity/activity/activity.info" || {
    echo "missing native GTK4 Help Activity bundle: $help_activity" >&2
    exit 2
}
test -f "$help_activity/activity/activity-help.svg" || {
    echo "missing native GTK4 Help Activity icon: $help_activity/activity/activity-help.svg" >&2
    exit 2
}
ln -sfn "$help_activity" "$activity_dir/Help.activity"
count_activity="$repo/packages/gtk4-count-activity"
test -f "$count_activity/activity/activity.info" || {
    echo "missing native GTK4 Count Activity bundle: $count_activity" >&2
    exit 2
}
test -f "$count_activity/countactivity4.py" || {
    echo "missing native GTK4 Count Activity entrypoint" >&2
    exit 2
}
ln -sfn "$count_activity" "$activity_dir/Count.activity"
calculate_activity="$repo/packages/gtk4-calculate-activity"
test -f "$calculate_activity/activity/activity.info" || {
    echo "missing native GTK4 Calculate Activity bundle: $calculate_activity" >&2
    exit 2
}
test -f "$calculate_activity/calculateactivity4.py" || {
    echo "missing native GTK4 Calculate Activity entrypoint" >&2
    exit 2
}
ln -sfn "$calculate_activity" "$activity_dir/Calculate.activity"
clock_activity="$repo/packages/gtk4-clock-activity"
test -f "$clock_activity/activity/activity.info" || {
    echo "missing native GTK4 Clock Activity bundle: $clock_activity" >&2
    exit 2
}
test -f "$clock_activity/clockactivity4.py" || {
    echo "missing native GTK4 Clock Activity entrypoint" >&2
    exit 2
}
ln -sfn "$clock_activity" "$activity_dir/Clock.activity"
jamclock_activity="$repo/packages/gtk4-jamclock-activity"
test -f "$jamclock_activity/activity/activity.info" || {
    echo "missing native GTK4 JAMClock Activity bundle: $jamclock_activity" >&2
    exit 2
}
test -f "$jamclock_activity/jamclockactivity4.py" || {
    echo "missing native GTK4 JAMClock Activity entrypoint" >&2
    exit 2
}
ln -sfn "$jamclock_activity" "$activity_dir/JAMClock.activity"
mastermind_activity="$repo/packages/gtk4-mastermind-activity"
test -f "$mastermind_activity/activity/activity.info" || {
    echo "missing native GTK4 Mastermind Activity bundle: $mastermind_activity" >&2
    exit 2
}
test -f "$mastermind_activity/mastermindactivity4.py" || {
    echo "missing native GTK4 Mastermind Activity entrypoint" >&2
    exit 2
}
ln -sfn "$mastermind_activity" "$activity_dir/Mastermind.activity"
poll_activity="$repo/packages/gtk4-poll-activity"
test -f "$poll_activity/activity/activity.info" || {
    echo "missing native GTK4 Poll Activity bundle: $poll_activity" >&2
    exit 2
}
test -f "$poll_activity/pollactivity4.py" || {
    echo "missing native GTK4 Poll Activity entrypoint" >&2
    exit 2
}
ln -sfn "$poll_activity" "$activity_dir/Poll.activity"
mancala_activity="$repo/packages/gtk4-mancala-activity"
test -f "$mancala_activity/activity/activity.info" || { echo "missing native GTK4 Mancala Activity bundle" >&2; exit 2; }
ln -sfn "$mancala_activity" "$activity_dir/Mancala.activity"
reversi_activity="$repo/packages/gtk4-reversi-activity"
test -f "$reversi_activity/activity/activity.info" || { echo "missing native GTK4 Reversi Activity bundle" >&2; exit 2; }
ln -sfn "$reversi_activity" "$activity_dir/Reversi.activity"
jumble_activity="$repo/packages/gtk4-jumble-activity"
test -f "$jumble_activity/activity/activity.info" || { echo "missing native GTK4 Jumble Activity bundle" >&2; exit 2; }
ln -sfn "$jumble_activity" "$activity_dir/Jumble.activity"
numberrush_activity="$repo/packages/gtk4-numberrush-activity"
test -f "$numberrush_activity/activity/activity.info" || { echo "missing native GTK4 Number Rush Activity bundle" >&2; exit 2; }
ln -sfn "$numberrush_activity" "$activity_dir/NumberRush.activity"
acrossdown_activity="$repo/packages/gtk4-acrossdown-activity"
test -f "$acrossdown_activity/activity/activity.info" || { echo "missing native GTK4 Across and Down Activity bundle" >&2; exit 2; }
ln -sfn "$acrossdown_activity" "$activity_dir/AcrossDown.activity"
iq_activity="$repo/packages/gtk4-iq-activity"
test -f "$iq_activity/activity/activity.info" || { echo "missing native GTK4 IQ Activity bundle" >&2; exit 2; }
ln -sfn "$iq_activity" "$activity_dir/IQ.activity"
appelhaken_activity="$repo/packages/gtk4-appelhaken-activity"
test -f "$appelhaken_activity/activity/activity.info" || { echo "missing native GTK4 Appel Haken Activity bundle" >&2; exit 2; }
ln -sfn "$appelhaken_activity" "$activity_dir/AppelHaken.activity"
ballandbrick_activity="$repo/packages/gtk4-ballandbrick-activity"
test -f "$ballandbrick_activity/activity/activity.info" || { echo "missing native GTK4 BallAndBrick Activity bundle" >&2; exit 2; }
ln -sfn "$ballandbrick_activity" "$activity_dir/BallAndBrick.activity"
implode_activity="$repo/packages/gtk4-implode-activity"
test -f "$implode_activity/activity/activity.info" || { echo "missing native GTK4 Implode Activity bundle" >&2; exit 2; }
ln -sfn "$implode_activity" "$activity_dir/Implode.activity"
playgo_activity="$repo/packages/gtk4-playgo-activity"
test -f "$playgo_activity/activity/activity.info" || { echo "missing native GTK4 PlayGo Activity bundle" >&2; exit 2; }
ln -sfn "$playgo_activity" "$activity_dir/PlayGo.activity"
blockparty_activity="$repo/packages/gtk4-blockparty-activity"
test -f "$blockparty_activity/activity/activity.info" || { echo "missing native GTK4 BlockParty Activity bundle" >&2; exit 2; }
ln -sfn "$blockparty_activity" "$activity_dir/BlockParty.activity"
typingturtle_activity="$repo/packages/gtk4-typingturtle-activity"
test -f "$typingturtle_activity/activity/activity.info" || { echo "missing native GTK4 Typing Turtle Activity bundle" >&2; exit 2; }
ln -sfn "$typingturtle_activity" "$activity_dir/TypingTurtle.activity"
memorize_activity="$repo/packages/gtk4-memorize-activity"
test -f "$memorize_activity/activity/activity.info" || { echo "missing native GTK4 Memorize Activity bundle" >&2; exit 2; }
ln -sfn "$memorize_activity" "$activity_dir/Memorize.activity"
maze_activity="$repo/packages/gtk4-maze-activity"
test -f "$maze_activity/activity/activity.info" || { echo "missing native GTK4 Maze Activity bundle" >&2; exit 2; }
ln -sfn "$maze_activity" "$activity_dir/Maze.activity"
fototoon_activity="$repo/packages/gtk4-fototoon-activity"
test -f "$fototoon_activity/activity/activity.info" || { echo "missing native GTK4 FotoToon Activity bundle" >&2; exit 2; }
ln -sfn "$fototoon_activity" "$activity_dir/FotoToon.activity"
portfolio_activity="$repo/packages/gtk4-portfolio-activity"
test -f "$portfolio_activity/activity/activity.info" || { echo "missing native GTK4 Portfolio Activity bundle" >&2; exit 2; }
ln -sfn "$portfolio_activity" "$activity_dir/Portfolio.activity"
markdown_activity="$repo/packages/gtk4-markdown-activity"
test -f "$markdown_activity/activity/activity.info" || { echo "missing native GTK4 Markdown Activity bundle" >&2; exit 2; }
ln -sfn "$markdown_activity" "$activity_dir/Markdown.activity"
finance_activity="$repo/packages/gtk4-finance-activity"
test -f "$finance_activity/activity/activity.info" || { echo "missing native GTK4 Finance Activity bundle" >&2; exit 2; }
ln -sfn "$finance_activity" "$activity_dir/Finance.activity"
words_activity="$repo/packages/gtk4-words-activity"
test -f "$words_activity/activity/activity.info" || { echo "missing native GTK4 Words Activity bundle" >&2; exit 2; }
ln -sfn "$words_activity" "$activity_dir/Words.activity"
lol_activity="$repo/packages/gtk4-last-one-loses-activity"
test -f "$lol_activity/activity/activity.info" || { echo "missing native GTK4 Last One Loses Activity bundle" >&2; exit 2; }
ln -sfn "$lol_activity" "$activity_dir/LastOneLoses.activity"
gtd_activity="$repo/packages/gtk4-gtd-activity"
test -f "$gtd_activity/activity/activity.info" || { echo "missing native GTK4 Get Things Done Activity bundle" >&2; exit 2; }
ln -sfn "$gtd_activity" "$activity_dir/GetThingsDone.activity"
gridpaint_activity="$repo/packages/gtk4-gridpaint-activity"
test -f "$gridpaint_activity/activity/activity.info" || { echo "missing native GTK4 Grid Paint Activity bundle" >&2; exit 2; }
ln -sfn "$gridpaint_activity" "$activity_dir/Gridpaint.activity"
stopwatch_activity="$repo/packages/gtk4-stopwatch-activity"
test -f "$stopwatch_activity/activity/activity.info" || { echo "missing native GTK4 Stopwatch Activity bundle" >&2; exit 2; }
ln -sfn "$stopwatch_activity" "$activity_dir/Stopwatch.activity"
gears_activity="$repo/packages/gtk4-gears-activity"
test -f "$gears_activity/activity/activity.info" || { echo "missing native GTK4 Gears Activity bundle" >&2; exit 2; }
ln -sfn "$gears_activity" "$activity_dir/Gears.activity"
turtleart_activity="$repo/packages/gtk4-turtleart-activity"
test -f "$turtleart_activity/activity/activity.info" || { echo "missing native GTK4 TurtleBlocks Activity bundle" >&2; exit 2; }
ln -sfn "$turtleart_activity" "$activity_dir/TurtleArt.activity"
gameoflife_activity="$repo/packages/gtk4-gameoflife-activity"
test -f "$gameoflife_activity/activity/activity.info" || { echo "missing native GTK4 Game Of Life Activity bundle" >&2; exit 2; }
ln -sfn "$gameoflife_activity" "$activity_dir/GameOfLife.activity"
colormyworld_activity="$repo/packages/gtk4-colormyworld-activity"
test -f "$colormyworld_activity/activity/activity.info" || { echo "missing native GTK4 Color My World Activity bundle" >&2; exit 2; }
ln -sfn "$colormyworld_activity" "$activity_dir/ColorMyWorld.activity"
abacus_activity="$repo/packages/gtk4-abacus-activity"
test -f "$abacus_activity/activity/activity.info" || { echo "missing native GTK4 Abacus Activity bundle" >&2; exit 2; }
ln -sfn "$abacus_activity" "$activity_dir/Abacus.activity"
planets_activity="$repo/packages/gtk4-planets-activity"
test -f "$planets_activity/activity/activity.info" || { echo "missing native GTK4 Planets Activity bundle" >&2; exit 2; }
ln -sfn "$planets_activity" "$activity_dir/Planets.activity"
write_activity="$repo/packages/gtk4-write-activity"
test -f "$write_activity/activity/activity.info" || { echo "missing native GTK4 Write Activity bundle" >&2; exit 2; }
ln -sfn "$write_activity" "$activity_dir/Write.activity"
connect_the_dots_activity="$repo/packages/gtk4-connect-the-dots-activity"
test -f "$connect_the_dots_activity/activity/activity.info" || { echo "missing native GTK4 Connect the Dots Activity bundle" >&2; exit 2; }
ln -sfn "$connect_the_dots_activity" "$activity_dir/ConnectTheDots.activity"
pippy_activity="$repo/packages/gtk4-pippy-activity"
test -f "$pippy_activity/activity/activity.info" || { echo "missing native GTK4 Pippy Activity bundle" >&2; exit 2; }
ln -sfn "$pippy_activity" "$activity_dir/Pippy.activity"
paint_activity="$repo/packages/gtk4-paint-activity"
test -f "$paint_activity/activity/activity.info" || { echo "missing native GTK4 Paint Activity bundle" >&2; exit 2; }
test -f "$paint_activity/paintactivity4.py" || { echo "missing native GTK4 Paint Activity entrypoint" >&2; exit 2; }
ln -sfn "$paint_activity" "$activity_dir/Paint.activity"
diamond_fusion_activity="$repo/packages/gtk4-diamond-fusion-activity"
test -f "$diamond_fusion_activity/activity/activity.info" || { echo "missing native GTK4 Diamond Fusion Activity bundle" >&2; exit 2; }
ln -sfn "$diamond_fusion_activity" "$activity_dir/DiamondFusion.activity"
level_activity="$repo/packages/gtk4-level-activity"
test -f "$level_activity/activity/activity.info" || { echo "missing native GTK4 Level Activity bundle" >&2; exit 2; }
test -f "$level_activity/levelactivity4.py" || { echo "missing native GTK4 Level Activity entrypoint" >&2; exit 2; }
ln -sfn "$level_activity" "$activity_dir/Level.activity"
moon_activity="$repo/packages/gtk4-moon-activity"
test -f "$moon_activity/activity/activity.info" || { echo "missing native GTK4 Moon Activity bundle" >&2; exit 2; }
ln -sfn "$moon_activity" "$activity_dir/Moon.activity"
get_books_activity="$repo/packages/gtk4-get-books-activity"
test -f "$get_books_activity/activity/activity.info" || { echo "missing native GTK4 Get Books Activity bundle" >&2; exit 2; }
test -f "$get_books_activity/getbooksactivity4.py" || { echo "missing native GTK4 Get Books Activity entrypoint" >&2; exit 2; }
ln -sfn "$get_books_activity" "$activity_dir/GetBooks.activity"
jukebox_activity="$repo/packages/gtk4-jukebox-activity"
test -f "$jukebox_activity/activity/activity.info" || { echo "missing native GTK4 Jukebox Activity bundle" >&2; exit 2; }
test -f "$jukebox_activity/jukeboxactivity4.py" || { echo "missing native GTK4 Jukebox Activity entrypoint" >&2; exit 2; }
ln -sfn "$jukebox_activity" "$activity_dir/Jukebox.activity"
read_activity="$repo/packages/gtk4-read-activity"
test -f "$read_activity/activity/activity.info" || { echo "missing native GTK4 Read Activity bundle" >&2; exit 2; }
test -f "$read_activity/readactivity4.py" || { echo "missing native GTK4 Read Activity entrypoint" >&2; exit 2; }
ln -sfn "$read_activity" "$activity_dir/Read.activity"
record_activity="$repo/packages/gtk4-record-activity"
test -f "$record_activity/activity/activity.info" || { echo "missing native GTK4 Record Activity bundle" >&2; exit 2; }
test -f "$record_activity/recordactivity4.py" || { echo "missing native GTK4 Record Activity entrypoint" >&2; exit 2; }
ln -sfn "$record_activity" "$activity_dir/Record.activity"
test -f "$native_terminal_activity/activity/activity.info" || {
    echo "missing native GTK4 Terminal Activity bundle: $native_terminal_activity" >&2
    exit 2
}
test -f "$native_terminal_activity/terminalactivity4.py" || {
    echo "missing native GTK4 Terminal Activity entrypoint" >&2
    exit 2
}
moon_activity="$repo/packages/gtk4-moon-activity"
test -f "$moon_activity/activity/activity.info" || { echo "missing native GTK4 Moon Activity bundle" >&2; exit 2; }
test -f "$moon_activity/moonactivity4.py" || { echo "missing native GTK4 Moon Activity entrypoint" >&2; exit 2; }
ln -sfn "$moon_activity" "$activity_dir/Moon.activity"
test -f "$imageviewer_activity/activity/activity.info" || {
    echo "missing pinned Image Viewer Activity bundle: $imageviewer_activity" >&2
    exit 2
}
ln -sfn "$imageviewer_activity" "$activity_dir/ImageViewer.activity"
ln -sfn "$native_terminal_activity" "$activity_dir/Terminal.activity"
test -f "$native_browse_activity/activity/activity.info" || {
    echo "missing native GTK4 Browse Activity bundle: $native_browse_activity" >&2
    exit 2
}
ln -sfn "$native_browse_activity" "$activity_dir/Browse.activity"

# Terminal and Browse/Help are native GTK4 activities; retired VTE/WebKit
# previews are no longer part of the modern runtime, so do not require those
# optional GTK3-era packages here.
for dep in 'gtk4 >= 4.22.2' 'wlroots-0.20 >= 0.20'; do
    pkg-config --exists "$dep" || { echo "missing guest build dependency: $dep"; exit 2; }
done

casilda_build="$root/build/casilda"
if [ -f "$casilda_build/build.ninja" ]; then
    meson setup --reconfigure "$casilda_build" "$casilda" --prefix="$prefix" --libdir=lib -Ddocumentation=false -Dvapi=false
else
    meson setup "$casilda_build" "$casilda" --prefix="$prefix" --libdir=lib --buildtype=debug -Ddocumentation=false -Dvapi=false
fi
meson compile -C "$casilda_build"
meson install -C "$casilda_build"
GI_TYPELIB_PATH="$prefix/lib/girepository-1.0" \
LD_LIBRARY_PATH="$prefix/lib" \
    "$venv/bin/python" -c 'import gi; gi.require_version("Casilda", "1.0"); from gi.repository import Casilda; print("Casilda 1.0: PASS", Casilda._version)'

ext_build="$root/build/sugar-ext"
if [ -f "$ext_build/build.ninja" ]; then
    meson setup --reconfigure "$ext_build" "$ext" --prefix="$prefix" --libdir=lib
else
    meson setup "$ext_build" "$ext" --prefix="$prefix" --libdir=lib --buildtype=debug
fi
meson compile -C "$ext_build"
meson install -C "$ext_build"

# Generate Jarabe's configuration with guest-local paths.  The GTK4 shell is
# Python, so stage its runtime data directly rather than invoking the currently
# broken upstream icon-distribution target (which references absent SVG files).
(
    cd "$shell"
    bash ./autogen.sh --prefix="$prefix" --disable-update-mimedb
)
install -d "$prefix/share/sugar/data" "$prefix/share/sugar/extensions"
cp -a "$shell/data/." "$prefix/share/sugar/data/"
cp -a "$shell/extensions/." "$prefix/share/sugar/extensions/"
test -f "$shell/src/jarabe/config.py"
grep -Fq "data_path = '$prefix/share/sugar/data'" "$shell/src/jarabe/config.py"

# sugar-artwork currently ships GTK3 CSS only.  Install the GTK4 port under
# the canonical Sugar theme names so both Jarabe and Activities resolve it
# through their existing gtk-theme-name setting.
for sugar_theme in sugar-72 sugar-100; do
    install -d "$prefix/share/themes/$sugar_theme/gtk-4.0"
    install -m 0644 "$repo/assets/gtk4/sugar.css" \
        "$prefix/share/themes/$sugar_theme/gtk-4.0/gtk.css"
done

# Keep mutable profile and schema state outside the source and prefix trees.
runroot="$root/runtime"
mkdir -p "$runroot/schemas"
cp "$shell/data/org.sugarlabs.gschema.xml" "$runroot/schemas/"
glib-compile-schemas "$runroot/schemas"
cp "$shell/data/group-labels.defaults" "$runroot/group-labels.json"

# The GTK4 Journal still consumes the upstream datastore D-Bus service.
# Build its small native metadata reader into the preview prefix only.
datastore_build="$root/build/sugar-datastore"
python_version=$($venv/bin/python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
datastore_site="$prefix/lib/python$python_version/site-packages"
mkdir -p "$datastore_build/carquinyol" "$datastore_site/carquinyol"
python_include=$($venv/bin/python -c 'import sysconfig; print(sysconfig.get_config_var("INCLUDEPY"))')
python_ext_suffix=$($venv/bin/python -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))')
gcc -shared -fPIC -O2 -I"$python_include" \
    -o "$datastore_build/carquinyol/metadatareader$python_ext_suffix" \
    "$datastore/src/carquinyol/metadatareader.c"
install -m 0755 "$datastore_build/carquinyol/metadatareader$python_ext_suffix" \
    "$datastore_site/carquinyol/"
cp "$datastore"/src/carquinyol/*.py "$datastore_site/carquinyol/"
PYTHONPATH="$datastore_site:$toolkit/src" "$venv/bin/python" -c \
    'import carquinyol.metadatareader; print("datastore metadata reader: PASS")'
echo "GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS"
echo "Wayland socket will be owned by embedded Casilda at runtime"
