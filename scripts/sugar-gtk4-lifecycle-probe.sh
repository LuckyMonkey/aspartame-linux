#!/usr/bin/env bash
set -euo pipefail

# Guest-only probe for the real Journal → Casilda Activity lifecycle.
if ! grep -qx 'IMAGE_ID=aspartame' /etc/os-release; then
    echo 'This probe is guest-only; run it inside the Aspartame VM.' >&2
    exit 2
fi

cycles=${1:-3}
case "$cycles" in
    ''|*[!0-9]*) echo 'usage: sugar-gtk4-lifecycle-probe.sh [cycles]' >&2; exit 2 ;;
esac
[ "$cycles" -gt 0 ] || { echo 'cycles must be positive' >&2; exit 2; }

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
        --method org.laptop.Journal.LaunchBundle org.laptop.HelpActivity '')
    activity_pid=''
    activity_id=''
    for _attempt in $(seq 1 50); do
        activity_pid=$(pgrep -u aspartame -f 'helpactivity4.HelpActivity' | head -1 || true)
        if [ -n "$activity_pid" ]; then
            activity_id=$(tr '\0' ' ' <"/proc/$activity_pid/cmdline" |
                sed -n 's/.*--activity-id \([^ ]*\).*/\1/p')
            [ -n "$activity_id" ] && break
        fi
        sleep 0.1
    done
    [ -n "$activity_id" ] || { echo "cycle=$cycle launch=FAIL" >&2; exit 1; }
    stop=$(aspartame_gdbus --dest org.laptop.Shell \
        --object-path /org/laptop/Shell \
        --method org.laptop.Shell.StopActivity "$activity_id")
    for _attempt in $(seq 1 50); do
        pgrep -u aspartame -f 'helpactivity4.HelpActivity' >/dev/null || break
        sleep 0.1
    done
    pgrep -u aspartame -f 'helpactivity4.HelpActivity' >/dev/null && {
        echo "cycle=$cycle cleanup=FAIL" >&2
        exit 1
    }
    echo "cycle=$cycle launch=$launch pid=$activity_pid activity_id=$activity_id stop=$stop cleanup=PASS"
done

echo 'lifecycle-probe=PASS'
