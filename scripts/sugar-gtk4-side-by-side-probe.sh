#!/usr/bin/env bash
set -euo pipefail

if ! grep -qx 'IMAGE_ID=aspartame' /etc/os-release; then
    echo 'This probe is guest-only; run it inside Aspartame.' >&2
    exit 2
fi
if [ "$(id -u)" -eq 0 ]; then
    echo 'Run this probe as the aspartame desktop user, not root.' >&2
    exit 2
fi

project_root=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
controller="$project_root/scripts/sugar-gtk4-space.sh"
workspace_tool="$project_root/scripts/sugar-x11-workspace.py"
# SSH/sudo callers can carry the root runtime directory into the desktop-user
# process. The controller owns the desktop user's runtime state, so derive
# this path from the effective UID rather than trusting inherited env.
runtime_dir="/run/user/$(id -u)"
export XDG_RUNTIME_DIR="$runtime_dir"
marker="$runtime_dir/aspartame-side-by-side"

[ -f "$marker" ] || {
    echo "side-by-side marker is missing: $marker" >&2
    exit 1
}

status=$(
    DISPLAY=${DISPLAY:-:0} GTK4_ROOT=${GTK4_ROOT:-/usr/lib/aspartame/gtk4-preview} \
        bash "$controller" status
)
gtk3_pid=$(printf '%s\n' "$status" | sed -n 's/^gtk3_pid=//p')
gtk4_pid=$(printf '%s\n' "$status" | sed -n 's/^gtk4_pid=//p')
[ "$gtk3_pid" != stopped ] && [ -n "$gtk3_pid" ] || {
    echo 'GTK3 shell PID is unavailable' >&2
    exit 1
}
[ "$gtk4_pid" != stopped ] && [ -n "$gtk4_pid" ] || {
    echo 'GTK4 shell PID is unavailable' >&2
    exit 1
}

inspect_window() {
    DISPLAY=${DISPLAY:-:0} "$workspace_tool" inspect --pid "$1" --timeout 30
}

gtk3_window=$(inspect_window "$gtk3_pid")
gtk4_window=$(inspect_window "$gtk4_pid")
screen_size=$(DISPLAY=${DISPLAY:-:0} xrandr --current 2>/dev/null | awk '
    / connected / {
        for (i = 1; i <= NF; i++) {
            if ($i ~ /^[0-9]+x[0-9]+\+/) {
                sub(/\+.*/, "", $i); print $i; exit
            }
        }
    }')
screen_size=${screen_size:-1920x1080}
screen_width=${screen_size%x*}
screen_height=${screen_size#*x}
half_width=$((screen_width / 2))

read_geometry() {
    printf '%s\n' "$1" | sed -n \
        's/^geometry=\(-*[0-9]*\),\(-*[0-9]*\) \([0-9]*\)x\([0-9]*\)$/\1 \2 \3 \4/p'
}
read -r gtk3_x gtk3_y gtk3_width gtk3_height <<<"$(read_geometry "$gtk3_window")"
read -r gtk4_x gtk4_y gtk4_width gtk4_height <<<"$(read_geometry "$gtk4_window")"
gtk3_workspace=$(printf '%s\n' "$gtk3_window" | sed -n 's/^workspace=//p')
gtk4_workspace=$(printf '%s\n' "$gtk4_window" | sed -n 's/^workspace=//p')

if [ "$gtk3_workspace" != 0 ] || [ "$gtk4_workspace" != 0 ] || \
   [ "$gtk3_x" != 0 ] || [ "$gtk3_y" != 0 ] || \
   [ "$gtk3_width" != "$half_width" ] || [ "$gtk3_height" != "$screen_height" ] || \
   [ "$gtk4_x" != "$half_width" ] || [ "$gtk4_y" != 0 ] || \
   [ "$gtk4_width" != "$((screen_width - half_width))" ] || \
   [ "$gtk4_height" != "$screen_height" ]; then
    echo "side-by-side=FAIL screen=${screen_width}x${screen_height}" >&2
    printf '%s\n' "$gtk3_window" "$gtk4_window" >&2
    exit 1
fi

printf 'side-by-side=PASS screen=%sx%s gtk3_pid=%s gtk4_pid=%s ' \
    "$screen_width" "$screen_height" "$gtk3_pid" "$gtk4_pid"
printf 'gtk3=%sx%s+%s+%s gtk4=%sx%s+%s+%s\n' \
    "$gtk3_width" "$gtk3_height" "$gtk3_x" "$gtk3_y" \
    "$gtk4_width" "$gtk4_height" "$gtk4_x" "$gtk4_y"
