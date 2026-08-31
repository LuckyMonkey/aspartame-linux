#!/usr/bin/env bash
set -euo pipefail

root=${GTK4_ROOT:-/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4}
shell="$root/sources/sugar"
toolkit="$root/sources/sugar-toolkit-gtk4"
prefix="$root/prefix"
runroot="$root/runtime-first-pixels"
log="$root/logs/gtk4-shell-$(date -u +%Y%m%dT%H%M%SZ).log"

for path in "$shell/src/jarabe/main.py" "$toolkit/src/sugar4" \
            "$prefix/lib/x86_64-linux-gnu/girepository-1.0/Casilda-0.1.typelib" \
            "$runroot/schemas/gschemas.compiled" "$runroot/group-labels.json"; do
    test -e "$path" || { echo "missing GTK4 preview requirement: $path" >&2; exit 2; }
done
command -v dbus-run-session >/dev/null || { echo "missing dbus-run-session" >&2; exit 2; }
command -v python3 >/dev/null || { echo "missing python3" >&2; exit 2; }

mkdir -p "$runroot/home" "$runroot/data" "$runroot/config" "$runroot/cache" "$root/logs"
chmod 700 "$runroot"

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

cat <<EOF
Aspartame GTK4 Sugar preview
  shell:   $(git -C "$shell" rev-parse HEAD)
  toolkit: $(git -C "$toolkit" rev-parse HEAD)
  display: $display
  runtime: $runroot
  log:     $log
EOF

exec dbus-run-session -- env \
    DISPLAY="$display" \
    SUGAR_HOME="$runroot/home" \
    SUGAR_PROFILE=default \
    XDG_RUNTIME_DIR="$runroot" \
    XDG_DATA_HOME="$runroot/data" \
    XDG_CONFIG_HOME="$runroot/config" \
    XDG_CACHE_HOME="$runroot/cache" \
    GSETTINGS_SCHEMA_DIR="$runroot/schemas" \
    SUGAR_GROUP_LABELS="$runroot/group-labels.json" \
    SUGAR_PROFILE_NAME=AspartameGTK4 \
    SUGAR_WINDOWED=1 \
    PYTHONPATH="$shell/src:$toolkit/src" \
    GI_TYPELIB_PATH="$prefix/lib/x86_64-linux-gnu/girepository-1.0" \
    LD_LIBRARY_PATH="$prefix/lib/x86_64-linux-gnu" \
    XDG_DATA_DIRS="$prefix/share:/usr/local/share:/usr/share" \
    python3 "$shell/src/jarabe/main.py" 2>&1 | tee "$log"
