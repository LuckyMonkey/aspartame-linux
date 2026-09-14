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
         "$share/packages/gtk4-numberrush-activity" \
         "$share/packages/gtk4-acrossdown-activity" \
         "$share/packages/gtk4-iq-activity" \
         "$share/packages/gtk4-appelhaken-activity" \
         "$share/packages/gtk4-ballandbrick-activity" \
         "$share/packages/gtk4-implode-activity" \
         "$share/packages/gtk4-playgo-activity" \
         "$share/packages/gtk4-blockparty-activity" \
         "$share/packages/gtk4-typingturtle-activity" \
         "$share/packages/gtk4-memorize-activity" \
         "$share/packages/gtk4-maze-activity" \
         "$share/packages/gtk4-fototoon-activity" \
         "$share/packages/gtk4-portfolio-activity" \
         "$share/packages/gtk4-markdown-activity" \
         "$share/packages/gtk4-finance-activity" \
         "$share/packages/gtk4-words-activity" \
         "$share/packages/gtk4-last-one-loses-activity" \
         "$share/packages/gtk4-gtd-activity" \
         "$share/packages/gtk4-gridpaint-activity" \
         "$share/packages/gtk4-stopwatch-activity" \
         "$share/packages/gtk4-gears-activity" \
         "$share/packages/gtk4-turtleart-activity" \
         "$share/packages/gtk4-gameoflife-activity" \
         "$share/packages/gtk4-colormyworld-activity" \
         "$share/packages/gtk4-abacus-activity" \
         "$share/packages/gtk4-planets-activity" \
         "$share/packages/gtk4-write-activity" \
         "$share/packages/gtk4-connect-the-dots-activity" \
         "$share/packages/gtk4-pippy-activity" \
         "$share/packages/gtk4-paint-activity" \
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
cp -a "$repo/packages/gtk4-numberrush-activity/." \
      "$share/packages/gtk4-numberrush-activity/"
cp -a "$repo/packages/gtk4-acrossdown-activity/." \
      "$share/packages/gtk4-acrossdown-activity/"
cp -a "$repo/packages/gtk4-iq-activity/." \
      "$share/packages/gtk4-iq-activity/"
cp -a "$repo/packages/gtk4-appelhaken-activity/." \
      "$share/packages/gtk4-appelhaken-activity/"
cp -a "$repo/packages/gtk4-ballandbrick-activity/." \
      "$share/packages/gtk4-ballandbrick-activity/"
cp -a "$repo/packages/gtk4-implode-activity/." \
      "$share/packages/gtk4-implode-activity/"
cp -a "$repo/packages/gtk4-playgo-activity/." \
      "$share/packages/gtk4-playgo-activity/"
cp -a "$repo/packages/gtk4-blockparty-activity/." \
      "$share/packages/gtk4-blockparty-activity/"
cp -a "$repo/packages/gtk4-typingturtle-activity/." \
      "$share/packages/gtk4-typingturtle-activity/"
cp -a "$repo/packages/gtk4-memorize-activity/." \
      "$share/packages/gtk4-memorize-activity/"
cp -a "$repo/packages/gtk4-maze-activity/." \
      "$share/packages/gtk4-maze-activity/"
cp -a "$repo/packages/gtk4-fototoon-activity/." \
      "$share/packages/gtk4-fototoon-activity/"
cp -a "$repo/packages/gtk4-portfolio-activity/." \
      "$share/packages/gtk4-portfolio-activity/"
cp -a "$repo/packages/gtk4-markdown-activity/." \
      "$share/packages/gtk4-markdown-activity/"
cp -a "$repo/packages/gtk4-finance-activity/." \
      "$share/packages/gtk4-finance-activity/"
cp -a "$repo/packages/gtk4-words-activity/." \
      "$share/packages/gtk4-words-activity/"
cp -a "$repo/packages/gtk4-last-one-loses-activity/." \
      "$share/packages/gtk4-last-one-loses-activity/"
cp -a "$repo/packages/gtk4-gtd-activity/." \
      "$share/packages/gtk4-gtd-activity/"
cp -a "$repo/packages/gtk4-gridpaint-activity/." \
      "$share/packages/gtk4-gridpaint-activity/"
cp -a "$repo/packages/gtk4-stopwatch-activity/." \
      "$share/packages/gtk4-stopwatch-activity/"
cp -a "$repo/packages/gtk4-gears-activity/." \
      "$share/packages/gtk4-gears-activity/"
cp -a "$repo/packages/gtk4-turtleart-activity/." \
      "$share/packages/gtk4-turtleart-activity/"
cp -a "$repo/packages/gtk4-gameoflife-activity/." \
      "$share/packages/gtk4-gameoflife-activity/"
cp -a "$repo/packages/gtk4-colormyworld-activity/." \
      "$share/packages/gtk4-colormyworld-activity/"
cp -a "$repo/packages/gtk4-abacus-activity/." \
      "$share/packages/gtk4-abacus-activity/"
cp -a "$repo/packages/gtk4-planets-activity/." \
      "$share/packages/gtk4-planets-activity/"
cp -a "$repo/packages/gtk4-write-activity/." \
      "$share/packages/gtk4-write-activity/"
cp -a "$repo/packages/gtk4-connect-the-dots-activity/." \
      "$share/packages/gtk4-connect-the-dots-activity/"
cp -a "$repo/packages/gtk4-pippy-activity/." \
      "$share/packages/gtk4-pippy-activity/"
cp -a "$repo/packages/gtk4-paint-activity/." \
      "$share/packages/gtk4-paint-activity/"
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
