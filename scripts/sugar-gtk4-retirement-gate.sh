#!/usr/bin/env bash
set -euo pipefail

root=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
classification="$root/docs/sugar-modernization/ACTIVITY_PORT_CLASSIFICATION.md"
share_report="$root/reports/gtk4/share-join-qualification-20261004.md"
chirality_report="$root/reports/gtk4/chirality-session-resume-implementation-20261004.md"

blockers=()
retirement_candidates=(
    "Portfolio" "Markdown" "Finance" "Write"
    "Pippy" "Jukebox" "Color My World" "Abacus"
)
missing_parity=()
for candidate in "${retirement_candidates[@]}"; do
    if ! awk -F'|' -v candidate="$candidate" \
        '$2 ~ "^[[:space:]]*" candidate "[[:space:]]*$" && $3 ~ /FULL PORT/ { found=1 }
         END { exit !found }' "$classification"; then
        missing_parity+=("$candidate")
    fi
done
if ((${#missing_parity[@]})); then
    blockers+=("full-parity")
fi
if [[ ! -f "$share_report" ]] ||
   ! grep -Eq 'peer room join[^[:cntrl:]]*PASS|share-join=PASS phase=join' "$share_report"; then
    blockers+=("collaboration-join")
fi
if [[ ! -f "$chirality_report" ]] ||
   ! grep -Eq 'chirality-resume=PASS|closes the shell/session-resume qualification' "$chirality_report"; then
    blockers+=("shell-session-restart")
fi

if ((${#blockers[@]})); then
    echo "gtk4-retirement=BLOCKED"
    printf 'blocker=%s\n' "${blockers[@]}"
    if ((${#missing_parity[@]})); then
        printf 'missing-full-parity=%s\n' "$(IFS=,; echo "${missing_parity[*]}")"
    fi
    printf 'evidence-share=%s\n' "${share_report#$root/}"
    printf 'evidence-chirality=%s\n' "${chirality_report#$root/}"
    echo "GTK3 fallback/reference packages remain installed."
    exit 1
fi

echo "gtk4-retirement=PASS"
echo "GTK3 package removal gates are closed; build a disposable image before removal."
