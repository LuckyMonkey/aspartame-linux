#!/usr/bin/env bash
set -euo pipefail

# Synchronize only GTK4 development inputs into the virtio share consumed by
# the guest. Generated guest build trees and runtime state remain untouched.
repo=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
share=${DEV_SHARE:-/media/freezer/SteamLibrary/vms/aspartame-build/runtime/aspartame-dev}

test -d "$share" || { echo "missing development share: $share" >&2; exit 2; }
mkdir -p "$share/patches/gtk4-preview" "$share/scripts" \
         "$share/packages/gtk4-help-activity" "$share/packages/gtk4-count-activity" \
         "$share/packages/gtk4-calculate-activity" \
         "$share/packages/gtk4-clock-activity" \
         "$share/packages/gtk4-jamclock-activity" \
         "$share/packages/gtk4-mastermind-activity" \
         "$share/packages/gtk4-poll-activity" \
         "$share/packages/gtk4-mancala-activity" \
         "$share/packages/gtk4-reversi-activity" \
         "$share/packages/gtk4-jumble-activity" \
         "$share/gtk4-overlay"

cp -a "$repo/patches/gtk4-preview/." "$share/patches/gtk4-preview/"
cp -a "$repo/scripts/." "$share/scripts/"
cp -a "$repo/packages/gtk4-help-activity/." \
      "$share/packages/gtk4-help-activity/"
cp -a "$repo/packages/gtk4-count-activity/." \
      "$share/packages/gtk4-count-activity/"
cp -a "$repo/packages/gtk4-calculate-activity/." \
      "$share/packages/gtk4-calculate-activity/"
cp -a "$repo/packages/gtk4-clock-activity/." \
      "$share/packages/gtk4-clock-activity/"
cp -a "$repo/packages/gtk4-jamclock-activity/." \
      "$share/packages/gtk4-jamclock-activity/"
cp -a "$repo/packages/gtk4-mastermind-activity/." \
      "$share/packages/gtk4-mastermind-activity/"
cp -a "$repo/packages/gtk4-poll-activity/." \
      "$share/packages/gtk4-poll-activity/"
cp -a "$repo/packages/gtk4-mancala-activity/." \
      "$share/packages/gtk4-mancala-activity/"
cp -a "$repo/packages/gtk4-reversi-activity/." \
      "$share/packages/gtk4-reversi-activity/"
cp -a "$repo/packages/gtk4-jumble-activity/." \
      "$share/packages/gtk4-jumble-activity/"
cp -a "$repo/gtk4-overlay/." "$share/gtk4-overlay/"
# Remove compatibility patches retired from the host tree so a persistent
# virtio share cannot replay stale staging decisions.
rm -f "$share/patches/gtk4-preview/0124-terminal-vte-compat.patch" \
      "$share/patches/gtk4-preview/0125-terminal-vte-typelib.patch"

printf 'GTK4 dev share synchronized: %s\n' "$share"
printf 'patches=%s scripts=%s help_icon=%s\n' \
    "$(find "$share/patches/gtk4-preview" -type f | wc -l)" \
    "$(find "$share/scripts" -maxdepth 1 -type f | wc -l)" \
    "$(test -f "$share/packages/gtk4-help-activity/activity/activity-help.svg" && echo PASS || echo FAIL)"
