#!/usr/bin/env bash
set -u

# Guest-side visual qualification. The host invokes this through the shared
# development tree; each activity is launched through the real Journal D-Bus
# route, given time to render, captured, and stopped before the next one.
if ! grep -qx 'IMAGE_ID=aspartame' /etc/os-release; then
    echo 'This sweep is guest-only; run it inside the Aspartame VM.' >&2
    exit 2
fi

root=${ASPARTAME_DEV_ROOT:-/mnt/aspartame-dev}
gtk4_root=${GTK4_ROOT:-/usr/lib/aspartame/gtk4-preview}
if [ ! -f "$root/scripts/sugar-gtk4-activity-matrix.sh" ]; then
    root="$gtk4_root"
fi
matrix="$root/scripts/sugar-gtk4-activity-matrix.sh"
out_dir=${1:-$root/reports/gtk4/visual-sweep-$(date +%Y%m%d)}
settle=${VISUAL_SETTLE_SECONDS:-0.8}
filter=${VISUAL_ACTIVITY_FILTER:-}
space_controller="$gtk4_root/scripts/sugar-gtk4-space.sh"

# A headless boot still owns separate GTK3/GTK4 workspaces. Select the modern
# Space before resolving its D-Bus address; the controller may start or
# re-present the GTK4 shell during initial session setup.
if [ -x "$space_controller" ]; then
    runuser -u aspartame -- env DISPLAY=:0 GTK4_ROOT="$gtk4_root" \
        bash "$space_controller" gtk4 >/dev/null 2>&1 || true
fi

resolution=$(runuser -u aspartame -- env DISPLAY=:0 xrandr --current |
    awk '/ connected / {
        for (field = 1; field <= NF; field++) {
            if ($field ~ /^[0-9]+x[0-9]+[+]/) {
                split($field, mode, "+")
                print mode[1]
                exit
            }
        }
    }')
shell_pattern='/sources/sugar/src/jarabe/main.py'
shell_pid=$(pgrep -u aspartame -f "$shell_pattern" | head -1 || true)
if [ -z "$shell_pid" ]; then
    echo 'GTK4 shell is not running' >&2
    exit 1
fi
dbus_address=$(tr '\0' '\n' <"/proc/$shell_pid/environ" |
    sed -n 's/^DBUS_SESSION_BUS_ADDRESS=//p')
if [ -z "$dbus_address" ]; then
    echo 'GTK4 D-Bus address unavailable' >&2
    exit 1
fi

mkdir -p "$out_dir"
if [ "$(id -u)" -eq 0 ]; then
    # The launcher is root-controlled because it must call the desktop user's
    # D-Bus session, but ffmpeg writes screenshots as `aspartame`.
    chown aspartame:aspartame "$out_dir" 2>/dev/null || true
fi
manifest="$out_dir/manifest.tsv"
printf 'bundle\tpattern\tstatus\tscreenshot\tnote\n' > "$manifest"

gdbus_call() {
    runuser -u aspartame -- env DBUS_SESSION_BUS_ADDRESS="$dbus_address" \
        gdbus call --timeout 5 --address "$dbus_address" "$@"
}

stop_activity() {
    local activity_id=${1:-}
    [ -n "$activity_id" ] || return 0
    gdbus_call --dest org.laptop.Shell --object-path /org/laptop/Shell \
        --method org.laptop.Shell.StopActivity "$activity_id" >/dev/null 2>&1 || true
    for _attempt in $(seq 1 50); do
        pgrep -u aspartame -f "${2:-$activity_id}" >/dev/null || return 0
        sleep 0.1
    done
    return 1
}

capture_one() {
    local bundle=$1 pattern=$2 slug=$3
    local activity_pid='' activity_id='' launch='' ready=0
    if pgrep -u aspartame -f "$pattern" >/dev/null; then
        echo "already-running:$pattern"
        return 1
    fi
    launch=$(gdbus_call --dest org.laptop.Journal --object-path /org/laptop/Journal \
        --method org.laptop.Journal.LaunchBundle "$bundle" '' 2>&1) || {
        echo "launch:$launch"
        return 1
    }
    for _attempt in $(seq 1 80); do
        activity_pid=$(pgrep -u aspartame -f "$pattern" | head -1 || true)
        if [ -n "$activity_pid" ]; then
            activity_id=$(tr '\0' ' ' <"/proc/$activity_pid/cmdline" |
                sed -n 's/.*--activity-id \([^ ]*\).*/\1/p')
            [ -n "$activity_id" ] && break
        fi
        sleep 0.1
    done
    if [ -z "$activity_id" ]; then
        echo 'activity-id-timeout'
        return 1
    fi
    for _attempt in $(seq 1 100); do
        owner=$(gdbus_call --dest org.freedesktop.DBus --object-path /org/freedesktop/DBus \
            --method org.freedesktop.DBus.GetConnectionUnixProcessID "org.laptop.Activity$activity_id" 2>/dev/null || true)
        if [ "$owner" = "(uint32 $activity_pid,)" ]; then
            active=$(gdbus_call --dest org.laptop.Shell --object-path /org/laptop/Shell \
                --method org.laptop.Shell.ActivateActivity "$activity_id" 2>/dev/null || true)
            responsive=$(gdbus_call --dest "org.laptop.Activity$activity_id" \
                --object-path "/org/laptop/Activity/${activity_id//-/_}" \
                --method org.laptop.Activity.SetActive true 2>/dev/null || true)
            if [ "$active" = "(true,)" ] && [ "$responsive" = "()" ]; then
                ready=1
                break
            fi
        fi
        sleep 0.1
    done
    if [ "$ready" -ne 1 ]; then
        stop_activity "$activity_id" "$pattern" || true
        echo 'activity-not-ready'
        return 1
    fi
    sleep "$settle"
    if ! kill -0 "$activity_pid" 2>/dev/null; then
        echo "activity-exited-before-screenshot pid=$activity_pid"
        return 1
    fi
    screenshot="$out_dir/$slug.png"
    if ! runuser -u aspartame -- env DISPLAY=:0 ffmpeg -hide_banner -loglevel error \
        -f x11grab -draw_mouse 0 -video_size "$resolution" -i :0 -frames:v 1 -y "$screenshot"; then
        stop_activity "$activity_id" "$pattern" || true
        echo 'screenshot-failed'
        return 1
    fi
    if ! stop_activity "$activity_id" "$pattern"; then
        echo "cleanup-failed:$activity_id"
        return 1
    fi
    echo "ready pid=$activity_pid activity-id=$activity_id screenshot=$screenshot launch=$launch"
    return 0
}

while IFS='|' read -r bundle pattern; do
    [ -n "$bundle" ] || continue
    if [ -n "$filter" ] && [[ ! "$bundle" =~ $filter ]]; then
        continue
    fi
    slug=${bundle//[^a-zA-Z0-9._-]/_}
    printf '== %s ==\n' "$bundle"
    if note=$(capture_one "$bundle" "$pattern" "$slug"); then
        printf '%s\t%s\tPASS\t%s/%s.png\t%s\n' "$bundle" "$pattern" "$out_dir" "$slug" "$note" >> "$manifest"
    else
        status=$?
        printf '%s\t%s\tFAIL\t\t%s\n' "$bundle" "$pattern" "$note" >> "$manifest"
        printf 'visual-sweep failure bundle=%s status=%s note=%s\n' "$bundle" "$status" "$note" >&2
    fi
done < <(sed -n "s/^    '\(.*\)'$/\1/p" "$matrix")

passes=$(awk -F '\t' 'NR > 1 && $3 == "PASS" {n++} END {print n + 0}' "$manifest")
failures=$(awk -F '\t' 'NR > 1 && $3 == "FAIL" {n++} END {print n + 0}' "$manifest")
printf 'visual-sweep=COMPLETE pass=%s fail=%s resolution=%s manifest=%s\n' \
    "$passes" "$failures" "$resolution" "$manifest"
[ "$failures" -eq 0 ]
