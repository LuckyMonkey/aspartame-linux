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
root=${GTK4_ROOT:-/home/aspartame/Development/gtk4-preview}
workspace_tool="$project_root/scripts/sugar-x11-workspace.py"
runner="$project_root/scripts/sugar-gtk4-run.sh"
action=${1:-toggle}

export DISPLAY=${DISPLAY:-:0}
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export ASPARTAME_GTK4_PREVIEW=1

# SSH and sudo commonly preserve a host/root bus address. Always bind this
# controller to the bus owned by the Metacity session it is configuring.
unset DBUS_SESSION_BUS_ADDRESS
session_pid=$(pgrep -u "$(id -u)" -x metacity | head -1 || true)
if [ -n "$session_pid" ] && [ -r "/proc/$session_pid/environ" ]; then
    while IFS= read -r -d '' entry; do
        case "$entry" in
            DBUS_SESSION_BUS_ADDRESS=*) export "$entry" ;;
        esac
    done < "/proc/$session_pid/environ"
fi
# Workspace switching uses EWMH and remains valid even when Metacity was
# launched without a session bus (common in recovery/reload sessions).  Only
# the optional gsettings keybinding setup needs D-Bus.
have_gsettings_bus=0
[ -n "${DBUS_SESSION_BUS_ADDRESS:-}" ] && have_gsettings_bus=1

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

require_gtk3() {
    local pid
    pid=$(gtk3_pid || true)
    [ -n "$pid" ] || {
        echo 'Cannot locate the GTK3 Sugar desktop.' >&2
        exit 1
    }
    "$workspace_tool" place --pid "$pid" --workspace 0 >/dev/null
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
    "$workspace_tool" place --pid "$pid" --workspace 1 --fullscreen >/dev/null
    GTK4_PID=$pid
}

select_gtk3() {
    require_gtk3
    "$workspace_tool" switch 0
    "$workspace_tool" activate --pid "$GTK3_PID" >/dev/null
}

select_gtk4() {
    start_gtk4
    "$workspace_tool" switch 1
    "$workspace_tool" activate --pid "$GTK4_PID" >/dev/null
}

case "$action" in
    setup)
        require_gtk3
        start_gtk4
        "$workspace_tool" switch 0
        "$workspace_tool" activate --pid "$GTK3_PID" >/dev/null
        echo 'Sugar Spaces ready: F7 = GTK3, F8 = GTK4'
        ;;
    gtk3)
        select_gtk3
        ;;
    gtk4)
        select_gtk4
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
        echo 'usage: sugar-gtk4-space.sh {setup|gtk3|gtk4|toggle|status}' >&2
        exit 2
        ;;
esac
