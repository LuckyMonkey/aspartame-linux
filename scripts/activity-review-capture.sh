#!/usr/bin/env bash
set -euo pipefail
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
activity=${1:-}
if [[ -z "$activity" || ! "$activity" =~ \.activity$ ]]; then
    echo "usage: $0 Bundle.activity" >&2
    exit 2
fi
source_dir="$root/packages/upstream-activities/$activity"
test -f "$source_dir/activity/activity.info" || { echo "unknown activity source: $activity" >&2; exit 1; }
source "$root/scripts/lib/sugar-vm.sh"
require_vm
bundle_id=$(awk -F' = ' '$1 == "bundle_id" {print $2}' "$source_dir/activity/activity.info")
out="$root/reports/activity-review/$bundle_id"
mkdir -p "$out"
stamp=$(date +%Y%m%d-%H%M%S)
vm_ssh "cat /usr/share/sugar/activities/$activity/activity/activity.info 2>/dev/null || true; ps -eo pid,args | grep '[s]ugar-activity' || true" > "$out/runtime-$stamp.txt"
SUGAR_SCREENSHOT_DIR="$out" "$root/scripts/sugar-screenshot.sh"
echo "activity review capture: $out"
