#!/usr/bin/env bash
set -euo pipefail

: "${DATASTORE_SERVICE:?DATASTORE_SERVICE is required}"
: "${DATASTORE_LOG:?DATASTORE_LOG is required}"
: "${SHELL_ENTRY:?SHELL_ENTRY is required}"
python_bin=${PYTHON_BIN:-python3}

"$python_bin" "$DATASTORE_SERVICE" >"$DATASTORE_LOG" 2>&1 &
datastore_pid=$!
cleanup() { kill "$datastore_pid" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

for attempt in $(seq 1 30); do
    if dbus-send --session --print-reply --dest=org.freedesktop.DBus \
        /org/freedesktop/DBus org.freedesktop.DBus.ListNames 2>/dev/null |
        grep -q "org.laptop.sugar.DataStore"; then
        echo "datastore: ready"
        break
    fi
    if ! kill -0 "$datastore_pid" 2>/dev/null; then
        echo "datastore: failed; see $DATASTORE_LOG" >&2
        exit 1
    fi
    sleep 0.1
done

exec "$python_bin" "$SHELL_ENTRY"
