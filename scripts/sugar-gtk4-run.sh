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

for path in "$shell/src/jarabe/main.py" "$toolkit/src/sugar4" \
            "$datastore/bin/datastore-service" \
            "$libdir/girepository-1.0/Casilda-1.0.typelib" \
            "$runroot/schemas/gschemas.compiled" "$runroot/group-labels.json"; do
    test -e "$path" || { echo "missing GTK4 preview requirement: $path" >&2; exit 2; }
done
metadata_reader=$(find "$datastore_site/carquinyol" -maxdepth 1 -name 'metadatareader*.so' -print -quit)
test -n "$metadata_reader" || { echo "missing GTK4 datastore metadata reader" >&2; exit 2; }
command -v dbus-run-session >/dev/null || { echo "missing dbus-run-session" >&2; exit 2; }
command -v python3 >/dev/null || { echo "missing python3" >&2; exit 2; }

mkdir -p "$runroot/home" "$runroot/data" "$runroot/config" "$runroot/cache" "$root/logs"
test -d "$prefix/share/sugar/extensions" || {
    echo "missing staged Sugar extensions: $prefix/share/sugar/extensions" >&2
    exit 2
}
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
    SUGAR_WINDOWED=1 \
    PYTHONPATH="$datastore_site:$datastore/src:$shell/src:$toolkit/src" \
    GI_TYPELIB_PATH="$libdir/girepository-1.0" \
    LD_LIBRARY_PATH="$libdir" \
    XDG_DATA_DIRS="$prefix/share:/usr/local/share:/usr/share" \
    DATASTORE_SERVICE="$datastore/bin/datastore-service" \
    DATASTORE_LOG="$root/logs/datastore-$(date -u +%Y%m%dT%H%M%SZ).log" \
    PYTHON_BIN="$python_bin" \
    SHELL_ENTRY="$shell/src/jarabe/main.py" \
    bash "$project_root/scripts/sugar-gtk4-session.sh"
