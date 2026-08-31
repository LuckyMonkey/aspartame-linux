#!/usr/bin/env bash
set -euo pipefail

root=${GTK4_ROOT:-/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4}
pins="$root/PINS.tsv"
test -f "$pins" || { echo "missing pin file: $pins" >&2; exit 1; }

fail=0
printf "%-24s %-8s %s\n" component status reference
while IFS=$'\t' read -r name url ref sha date; do
    [[ -z "$name" || "$name" == \#* ]] && continue
    remote=$(git ls-remote "$url" "$ref" | awk 'NR == 1 {print $1}')
    if [[ -n "$remote" && "$remote" == "$sha" ]]; then
        printf "%-24s %-8s %s\n" "$name" PASS "$ref@$sha"
    else
        display=$remote
        [[ -n "$display" ]] || display=missing
        printf "%-24s %-8s expected=%s remote=%s\n" "$name" FAIL "$ref@$sha" "$display"
        fail=1
    fi
done < "$pins"
exit "$fail"
