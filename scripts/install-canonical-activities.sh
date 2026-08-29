#!/usr/bin/env bash
set -euo pipefail
project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source "$project_root/scripts/lib/sugar-vm.sh"
share_root=${DEV_SHARE:-/media/freezer/SteamLibrary/vms/aspartame-build/runtime/aspartame-dev}
activity_root="$project_root/packages/upstream-activities"
require_vm
SUDO_ASKPASS=/tmp/aspartame-askpass sudo -A -v
while IFS=$'\t' read -r repo bundle; do
  test -n "$repo" || continue
  source="$activity_root/$repo"
  test -d "$source" && test -f "$source/activity/activity.info"
  SUDO_ASKPASS=/tmp/aspartame-askpass sudo -A rm -rf "$share_root/activities/$bundle"
  SUDO_ASKPASS=/tmp/aspartame-askpass sudo -A mkdir -p "$share_root/activities"
  SUDO_ASKPASS=/tmp/aspartame-askpass sudo -A cp -a "$source" "$share_root/activities/$bundle"
done < "$activity_root/INSTALL-MANIFEST"
SUDO_ASKPASS=/tmp/aspartame-askpass sudo -A install -m 0644 "$activity_root/INSTALL-MANIFEST" "$share_root/activities/INSTALL-MANIFEST"
# Remove only bundles previously installed by this experiment that failed runtime smoke tests.
for bundle in connect-the-dots.activity diamond-fusion.activity finance.activity gears.activity get-books.activity get-things-done.activity grid-paint.activity last-one-loses.activity level.activity markdown.activity moon.activity words.activity; do
  SUDO_ASKPASS=/tmp/aspartame-askpass sudo -A rm -rf "$share_root/activities/$bundle"
done
vm_ssh bash -s <<'REMOTE'
set -euo pipefail
while IFS=$'\t' read -r repo bundle; do
  test -n "$repo" || continue
  rm -rf "/usr/share/sugar/activities/$bundle"
  cp -a "/mnt/aspartame-dev/activities/$bundle" "/usr/share/sugar/activities/$bundle"
done < /mnt/aspartame-dev/activities/INSTALL-MANIFEST
for bundle in connect-the-dots.activity diamond-fusion.activity finance.activity gears.activity get-books.activity get-things-done.activity grid-paint.activity last-one-loses.activity level.activity markdown.activity moon.activity words.activity; do
  rm -rf "/usr/share/sugar/activities/$bundle"
done
REMOTE
printf 'Canonical source bundles deployed.\n'
