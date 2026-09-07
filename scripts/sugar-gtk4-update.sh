#!/usr/bin/env bash
set -euo pipefail
root=${GTK4_ROOT:-/home/aspartame/Development/gtk4-preview}
exec "$(dirname "$0")/sugar-upstream-sync.sh" "$root/sources/sugar" "$root/sources/sugar-toolkit-gtk4" "$root/sources/sugar-ext" "$root/sources/sugar-artwork" "$root/sources/sugar-datastore"
