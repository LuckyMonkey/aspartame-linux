#!/usr/bin/env bash
set -euo pipefail
project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source "$project_root/scripts/lib/sugar-vm.sh"
share_root=${DEV_SHARE:-/media/freezer/SteamLibrary/vms/aspartame-build/runtime/aspartame-dev}
activity_root="$project_root/packages/upstream-activities"
require_vm
SUDO_ASKPASS=/tmp/aspartame-askpass sudo -A -v
for spec in \
  'turtleart-activity:TurtleBlocks.activity' \
  'memorize-activity:Memorize.activity' \
  'maze-activity:Maze.activity'; do
  repo=${spec%%:*}; bundle=${spec##*:}
  test -f "$activity_root/$repo/activity/activity.info"
  SUDO_ASKPASS=/tmp/aspartame-askpass sudo -A rm -rf "$share_root/activities/$bundle"
  SUDO_ASKPASS=/tmp/aspartame-askpass sudo -A mkdir -p "$share_root/activities"
  SUDO_ASKPASS=/tmp/aspartame-askpass sudo -A cp -a "$activity_root/$repo" "$share_root/activities/$bundle"
done
vm_ssh bash -s <<'REMOTE'
set -euo pipefail
for bundle in TurtleBlocks.activity Memorize.activity Maze.activity; do
  rm -rf "/usr/share/sugar/activities/$bundle"
  cp -a "/mnt/aspartame-dev/activities/$bundle" "/usr/share/sugar/activities/$bundle"
  find "/usr/share/sugar/activities/$bundle" -type f -name '*.py' -exec chmod 0644 {} +
done
REMOTE
printf 'Installed canonical activity bundles:\n'
vm_ssh 'find /usr/share/sugar/activities -maxdepth 2 -type f -name activity.info | grep -E "TurtleBlocks|Memorize|Maze" | sort'
