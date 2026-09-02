#!/usr/bin/env bash
set -euo pipefail

project_root=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
root=${GTK4_ROOT:-/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4}
shell="$root/sources/sugar"
toolkit="$root/sources/sugar-toolkit-gtk4"
datastore="$root/sources/sugar-datastore"
datastore_site="$root/prefix/lib/python3.12/site-packages"
prefix="$root/prefix"
runroot="$root/runtime-first-pixels"
log="$root/logs/gtk4-shell-$(date -u +%Y%m%dT%H%M%SZ).log"
backend=${GTK4_BACKEND:-wayland}

case "$backend" in
    wayland|x11) ;;
    *) echo "GTK4_BACKEND must be wayland or x11 (got: $backend)" >&2; exit 2 ;;
esac

for path in "$shell/src/jarabe/main.py" "$toolkit/src/sugar4" \
            "$datastore/bin/datastore-service" \
            "$datastore_site/carquinyol/metadatareader.cpython-312-x86_64-linux-gnu.so" \
            "$prefix/lib/x86_64-linux-gnu/girepository-1.0/Casilda-0.1.typelib" \
            "$runroot/schemas/gschemas.compiled" "$runroot/group-labels.json"; do
    test -e "$path" || { echo "missing GTK4 preview requirement: $path" >&2; exit 2; }
done
command -v dbus-run-session >/dev/null || { echo "missing dbus-run-session" >&2; exit 2; }
command -v python3 >/dev/null || { echo "missing python3" >&2; exit 2; }

mkdir -p "$runroot/home" "$runroot/data" "$runroot/config" "$runroot/cache" "$root/logs"
# The shell config points at the preview prefix for extensions. Expose the
# pinned shell checkout there without installing anything system-wide.
mkdir -p "$prefix/share/sugar"
ln -sfn "$shell/extensions" "$prefix/share/sugar/extensions"
chmod 700 "$runroot"

display=${DISPLAY:-}
wayland_display=${WAYLAND_DISPLAY:-}
xvfb_pid=
if [ "$backend" = wayland ]; then
    if [ -z "${XDG_RUNTIME_DIR:-}" ] || [ ! -d "$XDG_RUNTIME_DIR" ]; then
        echo "Wayland preview requires an existing XDG_RUNTIME_DIR" >&2
        exit 2
    fi
    if [ -z "$wayland_display" ]; then
        echo "Wayland preview requires WAYLAND_DISPLAY (no outer compositor was found)" >&2
        echo "Use GTK4_BACKEND=x11 make sugar-gtk4-run for the diagnostic fallback." >&2
        exit 2
    fi
    test -S "$XDG_RUNTIME_DIR/$wayland_display" || {
        echo "Wayland socket not found: $XDG_RUNTIME_DIR/$wayland_display" >&2
        echo "Start an isolated Wayland compositor, then retry." >&2
        exit 2
    }
    ln -sfn "$XDG_RUNTIME_DIR/$wayland_display" "$runroot/$wayland_display"
    display=""
else
    if [ -z "$display" ]; then
        command -v Xvfb >/dev/null || { echo "DISPLAY is unset and Xvfb is unavailable" >&2; exit 2; }
        display=:99
        Xvfb "$display" -screen 0 1280x800x24 -nolisten tcp >"$root/logs/xvfb-gtk4-run.log" 2>&1 &
        xvfb_pid=$!
        trap 'kill "$xvfb_pid" 2>/dev/null || true' EXIT INT TERM
        sleep 1
    fi
fi

if [ "$backend" = wayland ]; then
    backend_env=(GDK_BACKEND=wayland DISPLAY= WAYLAND_DISPLAY="$wayland_display")
else
    backend_env=(GDK_BACKEND=x11 DISPLAY="$display" WAYLAND_DISPLAY=)
fi

cat <<EOF
Aspartame GTK4 Sugar preview
  shell:   $(git -C "$shell" rev-parse HEAD)
  toolkit: $(git -C "$toolkit" rev-parse HEAD)
  backend: $backend
  display: ${display:-none}
  wayland: ${wayland_display:-none}
  runtime: $runroot
  log:     $log
EOF

exec dbus-run-session -- env \
    "${backend_env[@]}" \
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
    SUGAR_WINDOWED="${SUGAR_WINDOWED:-1}" \
    PYTHONPATH="$datastore_site:$datastore/src:$shell/src:$toolkit/src" \
    GI_TYPELIB_PATH="$prefix/lib/x86_64-linux-gnu/girepository-1.0" \
    LD_LIBRARY_PATH="$prefix/lib/x86_64-linux-gnu" \
    XDG_DATA_DIRS="$prefix/share:/usr/local/share:/usr/share" \
    DATASTORE_SERVICE="$datastore/bin/datastore-service" \
    DATASTORE_LOG="$root/logs/datastore-$(date -u +%Y%m%dT%H%M%SZ).log" \
    SHELL_ENTRY="$shell/src/jarabe/main.py" \
    bash "$project_root/scripts/sugar-gtk4-session.sh"
