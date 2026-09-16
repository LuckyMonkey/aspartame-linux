#!/usr/bin/env bash
set -euo pipefail

# Guest-only probe for the real Journal → Casilda Activity lifecycle.
if ! grep -qx 'IMAGE_ID=aspartame' /etc/os-release; then
    echo 'This probe is guest-only; run it inside the Aspartame VM.' >&2
    exit 2
fi

cycles=${1:-3}
bundle_id=${2:-org.laptop.HelpActivity}
process_pattern=${3:-helpactivity4.HelpActivity}
case "$cycles" in
    ''|*[!0-9]*) echo 'usage: sugar-gtk4-lifecycle-probe.sh [cycles]' >&2; exit 2 ;;
esac
[ "$cycles" -gt 0 ] || { echo 'cycles must be positive' >&2; exit 2; }
[ -n "$bundle_id" ] && [ -n "$process_pattern" ] || {
    echo 'bundle and process pattern must be non-empty' >&2
    exit 2
}

# An instance left running from earlier work would otherwise be picked up as
# "the" Activity: the probe would stop that one, find the instance it actually
# launched still alive, and report a cleanup failure that says nothing about
# the lifecycle. Measure a clean launch instead of a misleading one.
if pgrep -u aspartame -f "$process_pattern" >/dev/null; then
    echo "An instance of $process_pattern is already running." >&2
    echo 'Stop it first; this probe measures a launch it owns.' >&2
    exit 2
fi

gtk4_pid=$(pgrep -u aspartame -f '/sources/sugar/src/jarabe/main.py' | head -1 || true)
[ -n "$gtk4_pid" ] || { echo 'GTK4 shell is not running' >&2; exit 1; }
dbus_address=$(tr '\0' '\n' <"/proc/$gtk4_pid/environ" |
    sed -n 's/^DBUS_SESSION_BUS_ADDRESS=//p')
[ -n "$dbus_address" ] || { echo 'GTK4 D-Bus address unavailable' >&2; exit 1; }

aspartame_gdbus() {
    runuser -u aspartame -- env DBUS_SESSION_BUS_ADDRESS="$dbus_address" \
        gdbus call --address "$dbus_address" "$@"
}

for cycle in $(seq 1 "$cycles"); do
    launch=$(aspartame_gdbus --dest org.laptop.Journal \
        --object-path /org/laptop/Journal \
        --method org.laptop.Journal.LaunchBundle "$bundle_id" '')
    activity_pid=''
    activity_id=''
    for _attempt in $(seq 1 50); do
        activity_pid=$(pgrep -u aspartame -f "$process_pattern" | head -1 || true)
        if [ -n "$activity_pid" ]; then
            activity_id=$(tr '\0' ' ' <"/proc/$activity_pid/cmdline" |
                sed -n 's/.*--activity-id \([^ ]*\).*/\1/p')
            [ -n "$activity_id" ] && break
        fi
        sleep 0.1
    done
    [ -n "$activity_id" ] || { echo "cycle=$cycle launch=FAIL" >&2; exit 1; }
    # A PID exists before Python imports or widget construction finish. Wait
    # for the Activity service and Jarabe's launch-completed state before Stop.
    # This establishes service readiness, not proof of rendered pixels.
    ready=0
    for _attempt in $(seq 1 100); do
        kill -0 "$activity_pid" 2>/dev/null || break
        owner=$(aspartame_gdbus --dest org.freedesktop.DBus \
            --object-path /org/freedesktop/DBus \
            --method org.freedesktop.DBus.GetConnectionUnixProcessID \
            "org.laptop.Activity$activity_id" 2>/dev/null || true)
        if [[ "$owner" == "(uint32 $activity_pid,)" ]]; then
            active=$(aspartame_gdbus --dest org.laptop.Shell \
                --object-path /org/laptop/Shell \
                --method org.laptop.Shell.ActivateActivity "$activity_id")
            responsive=$(aspartame_gdbus --timeout 5 \
                --dest "org.laptop.Activity$activity_id" \
                --object-path "/org/laptop/Activity/${activity_id//-/_}" \
                --method org.laptop.Activity.SetActive true 2>/dev/null || true)
            if [ "$active" = "(true,)" ] && [ "$responsive" = "()" ]; then
                ready=1
                break
            fi
        fi
        sleep 0.1
    done
    [ "$ready" -eq 1 ] || {
        echo "cycle=$cycle pid=$activity_pid activity_id=$activity_id service-ready=FAIL" >&2
        exit 1
    }
    echo "cycle=$cycle pid=$activity_pid service-ready=PASS shell-active=PASS"
    stop=$(aspartame_gdbus --dest org.laptop.Shell \
        --object-path /org/laptop/Shell \
        --method org.laptop.Shell.StopActivity "$activity_id")
    [ "$stop" = "(true,)" ] || {
        echo "cycle=$cycle pid=$activity_pid stop=$stop stop-request=FAIL" >&2
        exit 1
    }
    for _attempt in $(seq 1 50); do
        pgrep -u aspartame -f "$process_pattern" >/dev/null || break
        sleep 0.1
    done
    pgrep -u aspartame -f "$process_pattern" >/dev/null && {
        echo "cycle=$cycle cleanup=FAIL" >&2
        exit 1
    }
    echo "cycle=$cycle launch=$launch pid=$activity_pid activity_id=$activity_id stop=$stop cleanup=PASS"
done

echo 'lifecycle-probe=PASS'
