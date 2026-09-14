#!/usr/bin/env bash
set -euo pipefail

if ! grep -qx 'IMAGE_ID=aspartame' /etc/os-release; then
    echo 'This probe is guest-only; run it inside the Aspartame VM.' >&2
    exit 2
fi

declare -a activities=(
    'org.laptop.HelpActivity|helpactivity4.HelpActivity'
    'org.aspartame.Count|countactivity4.CountActivity'
    'org.aspartame.Calculate|calculateactivity4.CalculateActivity'
    'org.aspartame.Clock|clockactivity4.ClockActivity'
    'org.laptop.ImageViewerActivity|ImageViewerActivity.ImageViewerActivity'
    'org.laptop.Terminal|terminal.TerminalActivity'
    'org.laptop.WebActivity|webactivity.WebActivity'
    'org.laptop.Log|logviewer.LogActivity'
)

script_dir=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

for spec in "${activities[@]}"; do
    IFS='|' read -r bundle pattern <<< "$spec"
    echo "== $bundle =="
    "$script_dir/sugar-gtk4-lifecycle-probe.sh" 1 "$bundle" "$pattern"
done
echo 'activity-matrix=PASS'
