#!/usr/bin/env bash
set -euo pipefail

project_root=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
if ! grep -qx 'IMAGE_ID=aspartame' /etc/os-release; then
    echo 'This launcher is guest-only; run it inside the Aspartame development VM.' >&2
    exit 2
fi

root=${GTK4_ROOT:-/home/aspartame/Development/gtk4-preview}
shell="$root/sources/sugar"
toolkit="$root/sources/sugar-toolkit-gtk4"
datastore="$root/sources/sugar-datastore"
prefix="$root/prefix"
venv="$root/venv"
python_bin="$venv/bin/python"
test -x "$python_bin" || { echo "missing preview interpreter: $python_bin" >&2; exit 2; }
python_version=$($python_bin -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
datastore_site="$prefix/lib/python$python_version/site-packages"
libdir="$prefix/lib"
runroot=${GTK4_RUNTIME_ROOT:-$root/runtime}
log="$root/logs/gtk4-shell-$(date -u +%Y%m%dT%H%M%SZ).log"
: > "$log"
# Keep the session log authoritative while retaining normal launcher output.
exec > >(tee -a "$log") 2>&1

# Resolve the Journal window before starting the session. A distro GTK3 copy
# can otherwise win the namespace package and leave ShowJournal blank while
# the rest of the GTK4 shell appears healthy.
preview_pythonpath="$project_root/gtk4-overlay/src:$datastore_site:$datastore/src:$shell/src:$toolkit/src"
journal_window_path=$(PYTHONPATH="$preview_pythonpath" "$python_bin" -c \
    'import jarabe.journal.journalwindow as module; print(module.__file__)')
case "$journal_window_path" in
    "$shell/src/jarabe/journal/journalwindow.py"|"$project_root/gtk4-overlay/src/jarabe/journal/journalwindow.py") ;;
    *) echo "GTK4 Journal window resolved outside preview sources: $journal_window_path" >&2; exit 2 ;;
esac

for path in "$shell/src/jarabe/main.py" "$toolkit/src/sugar4" \
            "$datastore/bin/datastore-service" \
            "$libdir/girepository-1.0/Casilda-1.0.typelib" \
            "$runroot/schemas/gschemas.compiled" "$runroot/group-labels.json" \
            "$prefix/share/themes/sugar-72/gtk-4.0/gtk.css"; do
    test -e "$path" || { echo "missing GTK4 preview requirement: $path" >&2; exit 2; }
done
test -x "$venv/bin/sugar-activity4" || {
    echo "missing GTK4 Activity launcher: $venv/bin/sugar-activity4" >&2
    exit 2
}
test -f "$prefix/share/sugar/activities/Log.activity/activity/activity.info" || {
    echo "missing staged GTK4 Log Activity bundle" >&2
    exit 2
}
test -f "$prefix/share/sugar/activities/Help.activity/activity/activity.info" || {
    echo "missing staged GTK4 Help Activity bundle" >&2
    exit 2
}
test -f "$prefix/share/sugar/activities/Help.activity/activity/activity-help.svg" || {
    echo "missing staged GTK4 Help Activity icon" >&2
    exit 2
}
test -f "$project_root/gtk4-overlay/src/jarabe/journal/listview.py" || {
    echo "missing GTK4 native Journal overlay" >&2
    exit 2
}
metadata_reader=$(find "$datastore_site/carquinyol" -maxdepth 1 -name 'metadatareader*.so' -print -quit)
test -n "$metadata_reader" || { echo "missing GTK4 datastore metadata reader" >&2; exit 2; }
command -v dbus-run-session >/dev/null || { echo "missing dbus-run-session" >&2; exit 2; }
command -v python3 >/dev/null || { echo "missing python3" >&2; exit 2; }

mkdir -p "$runroot/home" "$runroot/data" "$runroot/config" "$runroot/cache" "$root/logs"
# Casilda exposes one private Activity compositor per modern Space. Refuse a
# second launcher before it can compete for the same fullscreen surface.
# The packaged runtime tree is read-only except for its explicit state
# subdirectories. Keep the process lock in the user-writable session tmpfs.
session_lock="${XDG_RUNTIME_DIR:-/tmp}/aspartame-gtk4-session.lock"
exec 9>"$session_lock"
flock -n 9 || {
    echo "GTK4 preview session already running (lock: $session_lock)" >&2
    exit 1
}
# The launcher is commonly invoked by root while the GTK4 session runs as the
# `aspartame` user.  Keep datastore/Xapian state user-owned so its lockfile can
# be opened on every restart (a previous root-owned index made Journal crash).
chown -R aspartame:aspartame "$runroot/home" "$runroot/data" \
    "$runroot/config" "$runroot/cache"
modern_activities="$runroot/activities"
mkdir -p "$modern_activities"
ln -sfn "$prefix/share/sugar/activities/Help.activity" \
    "$modern_activities/Help.activity"
test -d "$prefix/share/sugar/activities/Count.activity" || {
    echo "missing staged GTK4 Count Activity bundle" >&2
    exit 2
}
ln -sfn "$prefix/share/sugar/activities/Count.activity" \
    "$modern_activities/Count.activity"
test -d "$prefix/share/sugar/activities/Clock.activity" || {
    echo "missing staged GTK4 Clock Activity bundle" >&2
    exit 2
}
ln -sfn "$prefix/share/sugar/activities/Clock.activity" \
    "$modern_activities/Clock.activity"
test -d "$prefix/share/sugar/activities/JAMClock.activity" || {
    echo "missing staged GTK4 JAMClock Activity bundle" >&2
    exit 2
}
ln -sfn "$prefix/share/sugar/activities/JAMClock.activity" \
    "$modern_activities/JAMClock.activity"
# Keep every verified GTK4 bundle visible to the isolated Home registry.  If
# one is omitted here, duplicate GTK3 metadata can win the Home lookup even
# though the bundle was staged successfully by the build.
for modern_bundle in Calculate ImageViewer Terminal Browse Log Mastermind Poll Mancala Reversi Jumble NumberRush AcrossDown IQ AppelHaken BallAndBrick Implode PlayGo BlockParty TypingTurtle Memorize Maze FotoToon Portfolio Markdown Finance Words LastOneLoses GetThingsDone Gridpaint Stopwatch Gears TurtleArt GameOfLife ColorMyWorld Abacus Planets Write ConnectTheDots Pippy Paint DiamondFusion Level Moon GetBooks Jukebox Read; do
    test -d "$prefix/share/sugar/activities/${modern_bundle}.activity" || {
        echo "missing staged GTK4 ${modern_bundle} Activity bundle" >&2
        exit 2
    }
    ln -sfn "$prefix/share/sugar/activities/${modern_bundle}.activity" \
        "$modern_activities/${modern_bundle}.activity"
done
test -d "$prefix/share/sugar/extensions" || {
    echo "missing staged Sugar extensions: $prefix/share/sugar/extensions" >&2
    exit 2
}
# The packaged runtime root is read-only; only its state subdirectories are
# writable and are prepared above.

# Keep modern bundle resolution isolated from ~/Activities, where the stable
# GTK3 Help bundle otherwise wins duplicate bundle_id lookup.

display=${DISPLAY:-}
xvfb_pid=
if [ -z "$display" ]; then
    command -v Xvfb >/dev/null || { echo "DISPLAY is unset and Xvfb is unavailable" >&2; exit 2; }
    display=:99
    Xvfb "$display" -screen 0 1280x800x24 -nolisten tcp >"$root/logs/xvfb-gtk4-run.log" 2>&1 &
    xvfb_pid=$!
    trap 'kill "$xvfb_pid" 2>/dev/null || true' EXIT INT TERM
    sleep 1
fi

locale_name=${LANG:-C.UTF-8}
cat <<EOF
Aspartame GTK4 Sugar preview
  shell:   $(git -C "$shell" rev-parse HEAD)
  toolkit: $(git -C "$toolkit" rev-parse HEAD)
  display: $display
  runtime: $runroot
  log:     $log
EOF

# Keep GTK3-only sugar-overlay code out of the GTK4 interpreter. The
# overlay's jarabe.view modules import Gtk 3 and violate the process
# boundary when discovered through the extended jarabe package path.
exec env \
    ASPARTAME_GTK4_PREVIEW=1 \
    LANG="$locale_name" \
    DISPLAY="$display" \
    GDK_BACKEND=x11 \
    CASILDA_FORCE_SOFTWARE="${CASILDA_FORCE_SOFTWARE:-1}" \
    SUGAR_HOME="$runroot/home" \
    SUGAR_PROFILE=default \
    XDG_RUNTIME_DIR="$runroot" \
    XDG_DATA_HOME="$runroot/data" \
    XDG_CONFIG_HOME="$runroot/config" \
    XDG_CACHE_HOME="$runroot/cache" \
    GSETTINGS_SCHEMA_DIR="$runroot/schemas" \
    SUGAR_GROUP_LABELS="$runroot/group-labels.json" \
    SUGAR_MIME_DEFAULTS="$shell/data/mime.defaults" \
    SUGAR_PROFILE_NAME=AspartameGTK4 \
    SUGAR_ACTIVITIES_PATH="$modern_activities" \
    SUGAR_WINDOWED="${SUGAR_WINDOWED:-0}" \
    PYTHONPATH="$preview_pythonpath" \
    GI_TYPELIB_PATH="$libdir/girepository-1.0" \
    LD_LIBRARY_PATH="$libdir" \
    XDG_DATA_DIRS="$prefix/share:/usr/local/share:/usr/share" \
    DATASTORE_SERVICE="$datastore/bin/datastore-service" \
    DATASTORE_LOG="$root/logs/datastore-$(date -u +%Y%m%dT%H%M%SZ).log" \
    ASPARTAME_GTK4_LOG="$log" \
    PYTHON_BIN="$python_bin" \
    PATH="$venv/bin:$prefix/bin:$PATH" \
    SHELL_ENTRY="$shell/src/jarabe/main.py" \
    dbus-run-session -- \
    bash "$project_root/scripts/sugar-gtk4-session.sh"
