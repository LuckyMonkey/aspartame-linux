#!/usr/bin/env bash

project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
SSH_PORT=${SSH_PORT:-2222}
SSH_HOST=${SSH_HOST:-127.0.0.1}
SSH_USER=${SSH_USER:-root}
SSH_TARGET="$SSH_USER@$SSH_HOST"
SSH_CONTROL_PATH=${SSH_CONTROL_PATH:-/tmp/aspartame-ssh-${UID}-%C}
SSH_OPTS=(
    -o StrictHostKeyChecking=no
    -o UserKnownHostsFile=/dev/null
    -o ConnectTimeout=5
    -o ControlMaster=auto
    -o ControlPersist=120
    -o "ControlPath=$SSH_CONTROL_PATH"
    -p "$SSH_PORT"
)
# The development VM uses a temporary local askpass helper. Keep this
# opt-in and host-local; normal SSH setups continue to use their own agent.
if test -x /tmp/aspartame-askpass; then
    export SSH_ASKPASS=/tmp/aspartame-askpass
    export SSH_ASKPASS_REQUIRE=force
    export DISPLAY=${DISPLAY:-:0}
fi

SCP_OPTS=(
    -q
    -o StrictHostKeyChecking=no
    -o UserKnownHostsFile=/dev/null
    -o ConnectTimeout=5
    -o ControlMaster=auto
    -o ControlPersist=120
    -o "ControlPath=$SSH_CONTROL_PATH"
    -P "$SSH_PORT"
)

vm_ssh() {
    ssh "${SSH_OPTS[@]}" "$SSH_TARGET" "$@"
}

vm_scp_from() {
    local remote_path=$1 local_path=$2
    scp "${SCP_OPTS[@]}" "$SSH_TARGET:$remote_path" "$local_path"
}

require_vm() {
    if ! vm_ssh true >/dev/null 2>&1; then
        echo "Aspartame VM SSH is unavailable at $SSH_HOST:$SSH_PORT" >&2
        echo 'Start it with make run, then wait for the graphical session.' >&2
        return 1
    fi
}
