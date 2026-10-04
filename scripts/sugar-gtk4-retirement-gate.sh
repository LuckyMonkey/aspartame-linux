#!/usr/bin/env bash
set -euo pipefail

root=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
classification="$root/docs/sugar-modernization/ACTIVITY_PORT_CLASSIFICATION.md"
matrix="$root/docs/sugar-modernization/GTK4_ACTIVITY_MATRIX.md"
status="$root/docs/sugar-modernization/GTK4_STATUS.md"

blockers=()
if ! grep -Eq '^\|[^|]+\| FULL PORT \|' "$classification"; then
    blockers+=("full-parity")
fi
if grep -q "Activity join/action behavior" "$matrix"; then
    blockers+=("collaboration-join")
fi
if grep -q "full shell/session restart" "$status"; then
    blockers+=("shell-session-restart")
fi
if grep -q "Package removal is deliberately still blocked" "$matrix"; then
    blockers+=("fallback-removal-policy")
fi

if ((${#blockers[@]})); then
    echo "gtk4-retirement=BLOCKED"
    printf 'blocker=%s\n' "${blockers[@]}"
    echo "GTK3 fallback/reference packages remain installed."
    exit 1
fi

echo "gtk4-retirement=PASS"
echo "GTK3 package removal gates are closed; build a disposable image before removal."
