#!/usr/bin/env bash
set -euo pipefail

: "${DATASTORE_SERVICE:?DATASTORE_SERVICE is required}"
: "${DATASTORE_LOG:?DATASTORE_LOG is required}"
: "${SHELL_ENTRY:?SHELL_ENTRY is required}"
python_bin=${PYTHON_BIN:-python3}
resume_pid=

"$python_bin" "$DATASTORE_SERVICE" >"$DATASTORE_LOG" 2>&1 &
datastore_pid=$!
cleanup() {
    if [ -n "$resume_pid" ]; then
        kill "$resume_pid" 2>/dev/null || true
    fi
    kill "$datastore_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

datastore_ready=0
for attempt in $(seq 1 30); do
    if dbus-send --session --print-reply --dest=org.freedesktop.DBus \
        /org/freedesktop/DBus org.freedesktop.DBus.ListNames 2>/dev/null |
        grep -q "org.laptop.sugar.DataStore"; then
        echo "datastore: ready"
        datastore_ready=1
        break
    fi
    if ! kill -0 "$datastore_pid" 2>/dev/null; then
        echo "datastore: failed; see $DATASTORE_LOG" >&2
        exit 1
    fi
    sleep 0.1
done
if [ "$datastore_ready" -ne 1 ]; then
    echo "datastore: service name did not appear; see $DATASTORE_LOG" >&2
    exit 1
fi

"$python_bin" "$SHELL_ENTRY" &
shell_pid=$!

# Rehydrate only the explicit persistent Chirality state.  The helper waits
# for the new shell and Journal names, so it cannot race shell construction.
resume_script=${ASPARTAME_CHIRALITY_RESUME_SCRIPT:-}
resume_state=${ASPARTAME_CHIRALITY_STATE_FILE:-}
if [ -n "$resume_script" ] && [ -f "$resume_script" ] &&
   [ -n "$resume_state" ] && [ -f "$resume_state" ]; then
    "$python_bin" "$resume_script" --state-file "$resume_state" &
    resume_pid=$!
fi

set +e
wait "$shell_pid"
shell_status=$?
set -e
cleanup
exit "$shell_status"
