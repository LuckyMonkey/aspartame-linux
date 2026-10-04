#!/usr/bin/env bash
set -euo pipefail

# Single-surface bridge for the Chirality milestone.  A hand selects one
# complete Space; it never creates a pane or asks the comparison action to
# remain visible.  The current migration bridge maps Left/Right to the
# Classic/Modern shells.  Once GTK4 owns both Activities, only these target
# values need to change.
project_root=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
switcher=${ASPARTAME_SPACE_SWITCHER:-$project_root/scripts/sugar-gtk4-space.sh}

if [ ! -x "$switcher" ]; then
    echo "chirality: Spaces controller is not executable: $switcher" >&2
    exit 1
fi

case "${1:-}" in
    left)
        "$switcher" gtk3
        printf 'chirality-space=PASS side=left target=classic mode=single-surface\n'
        ;;
    right)
        "$switcher" gtk4
        printf 'chirality-space=PASS side=right target=modern mode=single-surface\n'
        ;;
    status)
        "$switcher" status
        ;;
    *)
        echo 'usage: sugar-chirality-space.sh {left|right|status}' >&2
        exit 2
        ;;
esac
