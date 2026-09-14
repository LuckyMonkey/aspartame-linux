#!/usr/bin/env bash
set -euo pipefail

# Synchronize only GTK4 development inputs into the virtio share consumed by
# the guest. Generated guest build trees and runtime state remain untouched.
repo=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
share=${DEV_SHARE:-/media/freezer/SteamLibrary/vms/aspartame-build/runtime/aspartame-dev}

test -d "$share" || { echo "missing development share: $share" >&2; exit 2; }
mkdir -p "$share/patches/gtk4-preview" "$share/scripts" \
         "$share/packages/gtk4-help-activity" "$share/packages/gtk4-count-activity" \
         "$share/gtk4-overlay"

cp -a "$repo/patches/gtk4-preview/." "$share/patches/gtk4-preview/"
cp -a "$repo/scripts/." "$share/scripts/"
cp -a "$repo/packages/gtk4-help-activity/." \
      "$share/packages/gtk4-help-activity/"
cp -a "$repo/packages/gtk4-count-activity/." \
      "$share/packages/gtk4-count-activity/"
cp -a "$repo/gtk4-overlay/." "$share/gtk4-overlay/"

printf 'GTK4 dev share synchronized: %s\n' "$share"
printf 'patches=%s scripts=%s help_icon=%s\n' \
    "$(find "$share/patches/gtk4-preview" -type f | wc -l)" \
    "$(find "$share/scripts" -maxdepth 1 -type f | wc -l)" \
    "$(test -f "$share/packages/gtk4-help-activity/activity/activity-help.svg" && echo PASS || echo FAIL)"
