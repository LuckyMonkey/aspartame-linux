#!/usr/bin/env bash
set -euo pipefail

if ! grep -qx 'IMAGE_ID=aspartame' /etc/os-release; then
    echo 'This controller is guest-only; run it inside Aspartame.' >&2
    exit 2
fi
if [ "$(id -u)" -eq 0 ]; then
    echo 'Run this controller as the desktop user, not root.' >&2
    exit 2
fi

project_root=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
default_root=/home/aspartame/Development/gtk4-preview
if [ -f "$project_root/STANDALONE-MANIFEST" ]; then
    default_root=$project_root
fi
root=${GTK4_ROOT:-$default_root}
workspace_tool="$project_root/scripts/sugar-x11-workspace.py"
runner="$project_root/scripts/sugar-gtk4-run.sh"
runtime_dir="/run/user/$(id -u)"
side_by_side_marker="$runtime_dir/aspartame-side-by-side"
action=${1:-toggle}

export DISPLAY=${DISPLAY:-:0}
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export ASPARTAME_GTK4_PREVIEW=1

# SSH and sudo commonly preserve a host/root bus address. Always bind this
# controller to the bus owned by the Metacity session it is configuring.
unset DBUS_SESSION_BUS_ADDRESS
session_pid=$(pgrep -u "$(id -u)" -x metacity | head -1 || true)
if [ -n "$session_pid" ] && [ -r "/proc/$session_pid/environ" ]; then
    session_env=$(tr '\0' '\n' < "/proc/$session_pid/environ" 2>/dev/null || true)
    while IFS= read -r entry; do
        case "$entry" in
            DBUS_SESSION_BUS_ADDRESS=*) export "$entry" ;;
        esac
    done <<< "$session_env"
fi
# Workspace switching uses EWMH and remains valid even when Metacity was
# launched without a session bus (common in recovery/reload sessions).  Only
# the optional gsettings keybinding setup needs D-Bus.
have_gsettings_bus=0
[ -n "${DBUS_SESSION_BUS_ADDRESS:-}" ] && have_gsettings_bus=1

record_space() {
    local space_id=$1
    local chirality_cli="$project_root/scripts/sugar-chirality.py"
    local state_file=${ASPARTAME_SPACES_STATE_FILE:-${XDG_RUNTIME_DIR}/aspartame/spaces.json}
    [ -f "$chirality_cli" ] || return 0
    python3 "$chirality_cli" --spaces-state-file "$state_file" \
        spaces-select "$space_id" >/dev/null
}

if [ "$have_gsettings_bus" -eq 1 ]; then
    workspace_count=$(gsettings get org.gnome.desktop.wm.preferences num-workspaces)
    if [ "$workspace_count" -lt 2 ]; then
        gsettings set org.gnome.desktop.wm.preferences num-workspaces 2
    fi
fi

# F1-F6 retain Sugar navigation. F7 and F8 select the two test spaces.
if [ "$have_gsettings_bus" -eq 1 ]; then
    gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-1 \
        "['F7', '<Super>Home']"
    gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-2 \
        "['F8']"
    key_one=$(gsettings get org.gnome.desktop.wm.keybindings switch-to-workspace-1)
    key_two=$(gsettings get org.gnome.desktop.wm.keybindings switch-to-workspace-2)
    if [[ "$key_one" != *F7* || "$key_two" != *F8* ]]; then
        echo 'Metacity keybindings unavailable; semantic Space switching remains enabled.' >&2
    fi
else
    echo 'Metacity session bus unavailable; semantic EWMH Space switching remains enabled.' >&2
fi

gtk4_pid() {
    local env_data
    for pid in $(pgrep -u "$(id -u)" -f 'python3 -m jarabe\.main|jarabe/main.py'); do
        [ -r "/proc/$pid/environ" ] || continue
        env_data=$(tr '\0' '\n' <"/proc/$pid/environ" 2>/dev/null) || continue
        printf '%s\n' "$env_data" | grep -qx 'ASPARTAME_GTK4_PREVIEW=1' || continue
        # A dead session bus can leave the Python process and fullscreen
        # surface alive while all semantic shell actions have stopped working.
        # Only report a modern Space PID while its private bus endpoint exists.
        bus_address=$(printf '%s\n' "$env_data" |
            sed -n 's/^DBUS_SESSION_BUS_ADDRESS=unix:path=\([^,]*\).*$/\1/p' | head -1)
        [ -n "$bus_address" ] && [ -S "$bus_address" ] || continue
        if command -v dbus-send >/dev/null 2>&1; then
            DBUS_SESSION_BUS_ADDRESS="unix:path=$bus_address" \
                timeout 2 dbus-send --session --print-reply=literal \
                --dest=org.laptop.Shell /org/laptop/Shell \
                org.freedesktop.DBus.Peer.Ping >/dev/null 2>&1 || continue
        fi
        echo "$pid"; return
    done
}

retire_stale_gtk4() {
    local pid bus_address env_data
    for pid in $(pgrep -u "$(id -u)" -f 'python3 -m jarabe\.main|jarabe/main.py'); do
        [ -r "/proc/$pid/environ" ] || continue
        env_data=$(tr '\0' '\n' <"/proc/$pid/environ" 2>/dev/null) || continue
        printf '%s\n' "$env_data" | grep -qx 'ASPARTAME_GTK4_PREVIEW=1' || continue
        bus_address=$(printf '%s\n' "$env_data" |
            sed -n 's/^DBUS_SESSION_BUS_ADDRESS=unix:path=\([^,]*\).*$/\1/p' | head -1)
        bus_ok=0
        if [ -n "$bus_address" ] && [ -S "$bus_address" ]; then
            if command -v dbus-send >/dev/null 2>&1 && ! \
                DBUS_SESSION_BUS_ADDRESS="unix:path=$bus_address" \
                timeout 2 dbus-send --session --print-reply=literal \
                --dest=org.laptop.Shell /org/laptop/Shell \
                org.freedesktop.DBus.Peer.Ping >/dev/null 2>&1; then
                bus_ok=1
            fi
        fi
        if [ "$bus_ok" -eq 1 ]; then
            echo "Retiring stale GTK4 shell PID $pid" >&2
            kill "$pid" 2>/dev/null || true
        fi
    done
}

gtk3_pid() {
    local env_data
    for pid in $(pgrep -u "$(id -u)" -f 'python3 -m jarabe\.main|jarabe/main.py'); do
        [ -r "/proc/$pid/environ" ] || continue
        env_data=$(tr '\0' '\n' <"/proc/$pid/environ" 2>/dev/null) || continue
        if ! printf '%s\n' "$env_data" | grep -q '^ASPARTAME_GTK4_PREVIEW=1$'; then
            echo "$pid"; return
        fi
    done
}

restart_gtk3() {
    local old_pid new_pid
    old_pid=$(gtk3_pid || true)
    [ -n "$old_pid" ] || {
        echo 'Cannot locate the GTK3 Sugar desktop.' >&2
        exit 1
    }
    kill "$old_pid" 2>/dev/null || true
    for _attempt in $(seq 1 300); do
        new_pid=$(gtk3_pid || true)
        if [ -n "$new_pid" ] && [ "$new_pid" != "$old_pid" ]; then
            GTK3_PID=$new_pid
            return 0
        fi
        sleep 0.1
    done
    echo 'GTK3 Sugar did not restart after Space layout change' >&2
    exit 1
}

all_gtk4_pids() {
    local pid env_data
    for pid in $(pgrep -u "$(id -u)" -f 'python3 -m jarabe\.main|jarabe/main.py'); do
        [ -r "/proc/$pid/environ" ] || continue
        env_data=$(tr '\0' '\n' <"/proc/$pid/environ" 2>/dev/null) || continue
        printf '%s\n' "$env_data" | grep -qx 'ASPARTAME_GTK4_PREVIEW=1' || continue
        echo "$pid"
    done
}

stop_gtk4() {
    local pid
    for pid in $(all_gtk4_pids); do
        echo "Stopping GTK4 shell PID $pid for windowed comparison" >&2
        kill "$pid" 2>/dev/null || true
    done
    for _attempt in $(seq 1 100); do
        if [ -z "$(all_gtk4_pids)" ]; then
            return 0
        fi
        sleep 0.1
    done
    echo 'GTK4 shell did not stop before side-by-side restart' >&2
    return 1
}

require_gtk3() {
    local pid
    pid=$(gtk3_pid || true)
    [ -n "$pid" ] || {
        echo 'Cannot locate the GTK3 Sugar desktop.' >&2
        exit 1
    }
    "$workspace_tool" place --pid "$pid" --workspace 0 \
        --timeout 30 >/dev/null
    GTK3_PID=$pid
}

start_gtk4() {
    local pid
    retire_stale_gtk4
    pid=$(gtk4_pid || true)
    if [ -z "$pid" ]; then
        # The modern Space owns a real fullscreen surface.  Starting it
        # windowed leaves a 1024x768 GTK surface letterboxed inside the
        # 1920x1080 guest and makes shell input/focus appear unreliable.
        setsid env GTK4_ROOT="$root" SUGAR_WINDOWED=0 \
            bash "$runner" > /tmp/aspartame-gtk4-current.log 2>&1 </dev/null &
        # GTK4 startup may activate portal/AT-SPI services before Jarabe
        # publishes its process marker. Allow a full 30 seconds so a healthy
        # modern Space is not reported as failed during cold startup.
        for _attempt in $(seq 1 300); do
            pid=$(gtk4_pid || true)
            [ -n "$pid" ] && break
            sleep 0.1
        done
    fi
    [ -n "$pid" ] || {
        echo 'GTK4 Sugar did not start; see /tmp/aspartame-gtk4-current.log' >&2
        exit 1
    }
    "$workspace_tool" place --pid "$pid" --workspace 1 --fullscreen \
        --timeout 30 >/dev/null
    GTK4_PID=$pid
}

start_gtk4_windowed() {
    local pid
    for pid in $(all_gtk4_pids); do
        local env_data
        env_data=$(tr '\0' '\n' <"/proc/$pid/environ" 2>/dev/null || true)
        if printf '%s\n' "$env_data" | grep -qx 'SUGAR_WINDOWED=1'; then
            GTK4_PID=$pid
            return 0
        fi
    done
    stop_gtk4
    setsid env GTK4_ROOT="$root" SUGAR_WINDOWED=1 \
        bash "$runner" > /tmp/aspartame-gtk4-side-by-side.log 2>&1 </dev/null &
    for _attempt in $(seq 1 300); do
        pid=$(gtk4_pid || true)
        [ -n "$pid" ] && break
        sleep 0.1
    done
    [ -n "${pid:-}" ] || {
        echo 'GTK4 windowed shell did not start; see /tmp/aspartame-gtk4-side-by-side.log' >&2
        exit 1
    }
    GTK4_PID=$pid
}

screen_size() {
    local mode
    mode=$(xrandr --current 2>/dev/null |
        awk '/ connected / { for (i = 1; i <= NF; i++) {
            if ($i ~ /^[0-9]+x[0-9]+\+/) { sub(/\+.*/, "", $i); print $i; exit }
        }}' || true)
    if [[ "$mode" =~ ^[0-9]+x[0-9]+$ ]]; then
        printf '%s\n' "$mode"
    else
        printf '1920x1080\n'
    fi
}

settle_workspace() {
    local expected=$1 current
    for _attempt in $(seq 1 40); do
        current=$("$workspace_tool" status |
            sed -n 's/^current=//p')
        if [ "$current" = "$expected" ]; then
            # Metacity publishes the desktop before the target surface is
            # focusable. Let that mapping complete before activation.
            sleep 0.25
            return 0
        fi
        sleep 0.05
    done
    echo "workspace $expected did not become current" >&2
    exit 1
}

select_side_by_side() {
    local dimensions screen_width screen_height half_width
    require_gtk3
    touch "$side_by_side_marker"
    restart_gtk3
    start_gtk4_windowed
    dimensions=$(screen_size)
    screen_width=${dimensions%x*}
    screen_height=${dimensions#*x}
    half_width=$((screen_width / 2))
    "$workspace_tool" place --pid "$GTK3_PID" --workspace 0 \
        --timeout 30 >/dev/null
    "$workspace_tool" place --pid "$GTK4_PID" --workspace 0 \
        --timeout 30 >/dev/null
    "$workspace_tool" geometry --pid "$GTK3_PID" --x 0 --y 0 \
        --width "$half_width" --height "$screen_height" --timeout 30 >/dev/null
    "$workspace_tool" geometry --pid "$GTK4_PID" --x "$half_width" --y 0 \
        --width "$((screen_width - half_width))" --height "$screen_height" \
        --timeout 30 >/dev/null
    # GTK4 may apply its windowed default size just after the first map.  A
    # second pass after that map keeps the semantic side-by-side action from
    # ending with a centred 1024x768 surface.
    sleep 0.5
    "$workspace_tool" geometry --pid "$GTK3_PID" --x 0 --y 0 \
        --width "$half_width" --height "$screen_height" --timeout 30 >/dev/null
    "$workspace_tool" geometry --pid "$GTK4_PID" --x "$half_width" --y 0 \
        --width "$((screen_width - half_width))" --height "$screen_height" \
        --timeout 30 >/dev/null
    "$workspace_tool" switch 0
    settle_workspace 0
    "$workspace_tool" activate --pid "$GTK4_PID" --timeout 30 >/dev/null
    printf 'Sugar Spaces side by side: GTK3=%sx%s GTK4=%sx%s\n' \
        "$half_width" "$screen_height" "$((screen_width - half_width))" "$screen_height"
}

select_gtk3() {
    if [ -f "$side_by_side_marker" ]; then
        rm -f "$side_by_side_marker"
        restart_gtk3
    fi
    require_gtk3
    "$workspace_tool" switch 0
    settle_workspace 0
    "$workspace_tool" activate --pid "$GTK3_PID" --timeout 30 >/dev/null
    record_space classic
}

select_gtk4() {
    if [ -f "$side_by_side_marker" ]; then
        rm -f "$side_by_side_marker"
        restart_gtk3
    fi
    start_gtk4
    "$workspace_tool" switch 1
    settle_workspace 1
    "$workspace_tool" activate --pid "$GTK4_PID" --timeout 30 >/dev/null
    record_space modern
}

case "$action" in
    setup)
        if [ -f "$side_by_side_marker" ]; then
            rm -f "$side_by_side_marker"
            restart_gtk3
        fi
        require_gtk3
        start_gtk4
        "$workspace_tool" switch 0
        settle_workspace 0
        "$workspace_tool" activate --pid "$GTK3_PID" --timeout 30 >/dev/null
        record_space classic
        echo 'Sugar Spaces ready: F7 = GTK3, F8 = GTK4'
        ;;
    gtk3)
        select_gtk3
        ;;
    gtk4)
        select_gtk4
        ;;
    side-by-side)
        select_side_by_side
        ;;
    toggle)
        current=$("$workspace_tool" status | sed -n 's/^current=//p')
        if [ "$current" -eq 0 ]; then
            select_gtk4
        else
            select_gtk3
        fi
        ;;
    status)
        "$workspace_tool" status
        pid=$(gtk3_pid || true)
        printf 'gtk3_pid=%s\n' "${pid:-stopped}"
        pid=$(gtk4_pid || true)
        printf 'gtk4_pid=%s\n' "${pid:-stopped}"
        printf 'keys=F7:GTK3,F8:GTK4\n'
        ;;
    *)
        echo 'usage: sugar-gtk4-space.sh {setup|gtk3|gtk4|side-by-side|toggle|status}' >&2
        exit 2
        ;;
esac
