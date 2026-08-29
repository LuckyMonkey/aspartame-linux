#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/sugar-vm.sh"
require_vm

old_state=$(vm_ssh /usr/local/bin/aspartame-sugar-state)
printf 'Aspartame full graphical-session restart\n'
printf '  Previous: %s\n' "$old_state"
printf '  Scope: tty1 login, Xorg, session D-Bus, Metacity, Sugar, Activities\n'
printf '  Persistent /home/aspartame is not unmounted or reformatted.\n'
vm_ssh pkill -u aspartame -f /usr/local/bin/aspartame-version-overlay || true
vm_ssh systemctl restart getty@tty1.service

health=''
for _ in $(seq 1 60); do
    if health=$(vm_ssh /usr/local/bin/aspartame-sugar-health 2>/dev/null); then
        break
    fi
    sleep 0.5
done
if ! grep -q '^Result: PASS$' <<<"$health"; then
    printf '%s\n' "$health" >&2
    echo 'Full session did not become healthy; run make sugar-logs.' >&2
    exit 1
fi
new_state=$(vm_ssh /usr/local/bin/aspartame-sugar-state)
printf '  New:      %s\n' "$new_state"
printf '%s\n' "$health"
