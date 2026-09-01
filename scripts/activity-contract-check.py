#!/usr/bin/env python3
"""Validate the Aspartame Activity catalog and runtime boundaries."""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEWS = ROOT / "docs/activity-reviews/REVIEWS.tsv"
NATIVE = {"native-sugar-bundle"}
WEB = {"sugarizer-web"}
STATES = {"unreviewed", "queued", "testing", "pass", "needs-work",
          "blocked", "remove-candidate"}
SHA = re.compile(r"^[0-9a-f]{40}$")

def main():
    with REVIEWS.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if not rows:
        raise SystemExit("activity contract: no catalog rows")
    ids = [row["bundle_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("activity contract: duplicate activity ID")
    formats = {}
    for row in rows:
        fmt = row["format"]
        formats[fmt] = formats.get(fmt, 0) + 1
        if fmt not in NATIVE | WEB:
            raise SystemExit("activity contract: unknown format {}".format(fmt))
        if row["run_status"] not in STATES:
            raise SystemExit("activity contract: invalid status {}".format(row["run_status"]))
        if row["rating"] and row["rating"] not in {"1", "2", "3", "4", "5"}:
            raise SystemExit("activity contract: invalid rating for {}".format(row["bundle_id"]))
        if not row["source_revision"]:
            raise SystemExit("activity contract: missing source revision for {}".format(row["bundle_id"]))
        if fmt in WEB and not SHA.fullmatch(row["source_revision"]):
            raise SystemExit("activity contract: invalid Sugarizer revision for {}".format(row["bundle_id"]))
        if fmt in NATIVE and not (ROOT / row["source_path"] / "activity/activity.info").is_file():
            raise SystemExit("activity contract: missing native source for {}".format(row["bundle_id"]))
    summary = ", ".join("{}={}".format(key, value) for key, value in sorted(formats.items()))
    print("activity contract: {} rows, {} unique IDs, {} PASS".format(len(rows), len(ids), summary))

if __name__ == "__main__":
    main()
