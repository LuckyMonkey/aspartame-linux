#!/usr/bin/env bash
set -euo pipefail

# GTK3 uses the same Journal/Shell D-Bus contract as the modern Space. Keep
# the lifecycle implementation shared, but identify the classic shell by its
# stable launcher and use the GTK3 Activity process by default.
script_dir=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
export SUGAR_LIFECYCLE_LABEL=GTK3
export SUGAR_LIFECYCLE_SHELL_PATTERN='^python3 -m jarabe\.main$'
export SUGAR_LIFECYCLE_ACTIVITY_ID_PATTERN='s/.* -a \([^ ]*\).*/\1/p'
export SUGAR_LIFECYCLE_STOP_MODE=signal
exec "$script_dir/sugar-gtk4-lifecycle-probe.sh" \
    "${1:-3}" "${2:-org.laptop.HelpActivity}" "${3:-helpactivity.HelpActivity}"
