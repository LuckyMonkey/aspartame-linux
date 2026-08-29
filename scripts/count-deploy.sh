#!/usr/bin/env bash
set -euo pipefail
project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source "$project_root/scripts/lib/sugar-vm.sh"
activity="$project_root/packages/aspartame-count/Count.activity"
share_root=${DEV_SHARE:-/media/freezer/SteamLibrary/vms/aspartame-build/runtime/aspartame-dev}
test -f "$activity/activity/activity.info"
python3 -m py_compile "$activity/activity.py"
rm -rf "$activity/__pycache__"
require_vm
SUDO_ASKPASS=/tmp/aspartame-askpass sudo -A -v
SUDO_ASKPASS=/tmp/aspartame-askpass sudo -A rm -rf "$share_root/activities/Count.activity"
SUDO_ASKPASS=/tmp/aspartame-askpass sudo -A mkdir -p "$share_root/activities"
SUDO_ASKPASS=/tmp/aspartame-askpass sudo -A cp -a "$activity" "$share_root/activities/Count.activity"
vm_ssh bash -s <<'REMOTE'
set -euo pipefail
rm -rf /usr/share/sugar/activities/Count.activity
install -d /usr/share/sugar/activities
cp -a /mnt/aspartame-dev/activities/Count.activity /usr/share/sugar/activities/Count.activity
find /usr/share/sugar/activities/Count.activity -type f -exec chmod 0644 {} +
chmod 0755 /usr/share/sugar/activities/Count.activity/activity.py
REMOTE
printf 'Count Activity deployed to /usr/share/sugar/activities/Count.activity\n'
