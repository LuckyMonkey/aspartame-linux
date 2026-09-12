#!/usr/bin/env bash
set -euo pipefail

fail() {
    echo "sugar-gtk4-runtime-check: $*" >&2
    exit 1
}

target=${1:-}
case "$target" in
    gtk3) expected_desktop=0 ;;
    gtk4) expected_desktop=1 ;;
    *) echo 'usage: sugar-gtk4-runtime-check.sh {gtk3|gtk4}' >&2; exit 2 ;;
esac

os_release=${ASPARTAME_OS_RELEASE:-/etc/os-release}
grep -qx 'IMAGE_ID=aspartame' "$os_release" ||
    fail 'this check only runs inside Aspartame'
[ "$(id -u)" -ne 0 ] || fail 'run as the desktop user, not root'
command -v xprop >/dev/null || fail 'xprop is required'

project_root=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
root=${GTK4_ROOT:-/home/aspartame/Development/gtk4-preview}
runtime=${GTK4_RUNTIME_ROOT:-$root/runtime}
workspace_tool=${ASPARTAME_WORKSPACE_TOOL:-$project_root/scripts/sugar-x11-workspace.py}
proc_root=${ASPARTAME_PROC_ROOT:-/proc}
log=${ASPARTAME_GTK4_LOG:-/tmp/aspartame-gtk4-current.log}
log_lines=${ASPARTAME_GTK4_LOG_LINES:-400}
export DISPLAY=${DISPLAY:-:0}
export XDG_RUNTIME_DIR=/run/user/$(id -u)

case "$log_lines" in
    ''|*[!0-9]*) fail 'ASPARTAME_GTK4_LOG_LINES must be a positive integer' ;;
    0) fail 'ASPARTAME_GTK4_LOG_LINES must be greater than zero' ;;
esac
[ -x "$workspace_tool" ] || fail "workspace helper is not executable: $workspace_tool"

stable_pids=$(pgrep -u "$(id -u)" -f '^python3 -m jarabe\.main$' || true)
gtk4_pids=$(pgrep -u "$(id -u)" -f \
    "^$root/venv/bin/python $root/sources/sugar/src/jarabe/main.py$" || true)

one_pid() {
    local label=$1 pids=$2 count
    count=$(printf '%s\n' "$pids" | awk 'NF { count++ } END { print count + 0 }')
    [ "$count" -eq 1 ] || fail "expected one $label process, found $count"
    printf '%s\n' "$pids"
}

case "$target" in
    gtk3) target_pid=$(one_pid 'GTK3 Sugar' "$stable_pids") ;;
    gtk4) target_pid=$(one_pid 'GTK4 Sugar' "$gtk4_pids") ;;
esac

status=$("$workspace_tool" status)
current=$(printf '%s\n' "$status" | sed -n 's/^current=//p')
[ "$current" = "$expected_desktop" ] ||
    fail "$target expects desktop $expected_desktop; current desktop is ${current:-unknown}"

active_window=$(xprop -root _NET_ACTIVE_WINDOW | sed -n \
    's/.*# \(0x[[:xdigit:]]\+\).*/\1/p')
[ -n "$active_window" ] && [ "$active_window" != 0x0 ] ||
    fail 'the window manager has no active window'
active_pid=$(xprop -id "$active_window" _NET_WM_PID | sed -n \
    's/.* = \([0-9][0-9]*\)$/\1/p')
active_desktop=$(xprop -id "$active_window" _NET_WM_DESKTOP | sed -n \
    's/.* = \([0-9][0-9]*\)$/\1/p')
[ "$active_pid" = "$target_pid" ] ||
    fail "active window $active_window belongs to PID ${active_pid:-unknown}, not $target_pid"
[ "$active_desktop" = "$expected_desktop" ] ||
    fail "active target is on desktop ${active_desktop:-unknown}, not $expected_desktop"

if [ "$target" = gtk4 ]; then
    socket=$runtime/wayland-sugar
    [ -S "$socket" ] || fail "private Wayland socket is missing: $socket"
    [ "$(stat -c %u "$runtime")" = "$(id -u)" ] ||
        fail 'GTK4 runtime is not owned by the desktop user'
    [ "$(stat -c %a "$runtime")" = 700 ] ||
        fail 'GTK4 runtime permissions are not private (expected 700)'
    [ -r "$proc_root/$target_pid/environ" ] ||
        fail "cannot inspect GTK4 process environment for PID $target_pid"
    tr '\0' '\n' < "$proc_root/$target_pid/environ" |
        grep -Fxq "XDG_RUNTIME_DIR=$runtime" ||
        fail 'GTK4 process does not own the expected private runtime'
    if [ ! -r "$log" ]; then
        log=$(ls -t "$root/logs"/gtk4-shell-*.log 2>/dev/null | head -1 || true)
    fi
    [ -n "$log" ] && [ -r "$log" ] || fail "GTK4 session log is missing"
fi

if [ -r "$log" ] && tail -n "$log_lines" "$log" | grep -Eiq \
    'Traceback \(most recent call last\)|Segmentation fault|segfault at|SIGSEGV|Fatal Python error|core dumped'; then
    fail "fatal marker found in the last $log_lines lines of $log"
fi

stable_summary=$(printf '%s\n' "$stable_pids" | awk 'NF' | paste -sd, -)
gtk4_summary=$(printf '%s\n' "$gtk4_pids" | awk 'NF' | paste -sd, -)
printf 'runtime-check=ok target=%s pid=%s desktop=%s window=%s stable_pid=%s gtk4_pid=%s\n' \
    "$target" "$target_pid" "$current" "$active_window" \
    "${stable_summary:-stopped}" "${gtk4_summary:-stopped}"
