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
session_pid=$(pgrep -u "$(id -u)" -x metacity | head -1)
[ -n "$session_pid" ] || {
    echo 'Cannot locate the Metacity session bus.' >&2
    exit 2
}
while IFS= read -r -d '' entry; do
    case "$entry" in
        DBUS_SESSION_BUS_ADDRESS=*) export "$entry" ;;
    esac
done < "/proc/$session_pid/environ"
[ -n "${DBUS_SESSION_BUS_ADDRESS:-}" ] || {
    echo 'Metacity has no D-Bus session address.' >&2
    exit 2
}

workspace_count=$(gsettings get org.gnome.desktop.wm.preferences num-workspaces)
if [ "$workspace_count" -lt 2 ]; then
    gsettings set org.gnome.desktop.wm.preferences num-workspaces 2
fi

# F1-F6 retain Sugar navigation. F7 and F8 select the two test spaces.
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-1 \
    "['F7', '<Super>Home']"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-2 \
    "['F8']"
key_one=$(gsettings get org.gnome.desktop.wm.keybindings switch-to-workspace-1)
key_two=$(gsettings get org.gnome.desktop.wm.keybindings switch-to-workspace-2)
if [[ "$key_one" != *F7* || "$key_two" != *F8* ]]; then
    echo 'Metacity keybindings unavailable; semantic Space switching remains enabled.' >&2
fi

gtk4_pid() {
    for pid in $(pgrep -u "$(id -u)" -f 'python3 -m jarabe\.main|jarabe/main.py'); do
        tr '\0' '\n' <"/proc/$pid/environ" 2>/dev/null |
            grep -qx 'ASPARTAME_GTK4_PREVIEW=1' && { echo "$pid"; return; }
    done
}

gtk3_pid() {
    for pid in $(pgrep -u "$(id -u)" -f 'python3 -m jarabe\.main|jarabe/main.py'); do
        if ! tr '\0' '\n' <"/proc/$pid/environ" 2>/dev/null |
            grep -q '^ASPARTAME_GTK4_PREVIEW=1$'; then
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
    pid=$(gtk4_pid || true)
    if [ -z "$pid" ]; then
        # The modern Space owns a real fullscreen surface.  Starting it
        # windowed leaves a 1024x768 GTK surface letterboxed inside the
        # 1920x1080 guest and makes shell input/focus appear unreliable.
        setsid env GTK4_ROOT="$root" SUGAR_WINDOWED=0 \
            bash "$runner" > /tmp/aspartame-gtk4-current.log 2>&1 </dev/null &
        for _attempt in $(seq 1 100); do
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
