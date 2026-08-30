#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
capture_output=$("$project_root/scripts/sugar-screenshot.sh")
printf '%s\n' "$capture_output"
screenshot=$(sed -n 's/^Screenshot: //p' <<<"$capture_output" | tail -n 1)
test -n "$screenshot" && test -s "$screenshot"

source "$project_root/scripts/lib/sugar-vm.sh"
health=$(vm_ssh /usr/local/bin/aspartame-sugar-health 2>&1)
if ! grep -q '^Result: PASS$' <<<"$health"; then
    printf '%s\n' "$health" >&2
    echo 'Sugar failed health checks; run make sugar-logs' >&2
    exit 12
fi

state=$(vm_ssh /usr/local/bin/aspartame-sugar-state)
printf '\nRuntime state:\n  %s\n\n' "$state"
printf '%s\n' "$health"

ocr_file="${screenshot%.png}.txt"
if test -n "${EXPECT_VISIBLE_TEXT:-}"; then
    test -r "$ocr_file" || { echo 'OCR output is unavailable' >&2; exit 13; }
    if ! grep -Fq -- "$EXPECT_VISIBLE_TEXT" "$ocr_file"; then
        printf 'Expected visible text was not found: %s\n' "$EXPECT_VISIBLE_TEXT" >&2
        printf 'OCR output: %s\n' "$ocr_file" >&2
        exit 14
    fi
    printf 'Expected visible text: PASS (%s)\n' "$EXPECT_VISIBLE_TEXT"
else
    printf 'Expected visible text: not requested (set EXPECT_VISIBLE_TEXT=...)\n'
fi

printf '\nVisual check: PASS\nScreenshot: %s\n' "$screenshot"
