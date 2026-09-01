#!/usr/bin/env bash
set -euo pipefail
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
manifest="$root/packages/upstream-activities/INSTALL-MANIFEST"
revisions="$root/packages/upstream-activities/REVISION-MANIFEST"
reviews="$root/docs/activity-reviews/REVIEWS.tsv"
fail=0
while IFS=$'\t' read -r source bundle; do
    [[ -z "$source" || "$source" == \#* ]] && continue
    test -f "$root/packages/upstream-activities/$source/activity/activity.info" || { echo "missing activity.info: $source"; fail=1; }
    grep -q "^$source[[:space:]]" "$revisions" || { echo "missing revision: $source"; fail=1; }
done < "$manifest"
python3 "$root/scripts/activity-review-inventory.py" >/dev/null
python3 "$root/scripts/activity-contract-check.py"
python3 - "$reviews" <<'PY'
import csv, sys
with open(sys.argv[1], newline="") as stream:
    rows = list(csv.DictReader(stream, delimiter="\t"))
allowed = {"unreviewed", "queued", "testing", "pass", "needs-work", "blocked", "remove-candidate"}
assert rows
for row in rows:
    assert row["run_status"] in allowed, row
    if row["rating"]:
        assert row["rating"] in {"1","2","3","4","5"}, row
print(f"review rows: {len(rows)} PASS")
PY
exit "$fail"
