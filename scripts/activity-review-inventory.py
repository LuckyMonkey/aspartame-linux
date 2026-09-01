#!/usr/bin/env python3
from configparser import ConfigParser
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "packages/upstream-activities/INSTALL-MANIFEST"
REVISIONS = ROOT / "packages/upstream-activities/REVISION-MANIFEST"
REVIEWS = ROOT / "docs/activity-reviews/REVIEWS.tsv"
SUGARIZER_CATALOG = ROOT / "packages/sugarizer/activities.json"
SUGARIZER_REVISION = ROOT / "packages/sugarizer/REVISION"
FIELDS = ["bundle_id", "name", "version", "source_revision", "source_path", "format", "run_status", "rating", "notes", "last_tested", "screenshot"]

def read_revisions():
    result = {}
    for line in REVISIONS.read_text().splitlines():
        parts = line.split("\t")
        if len(parts) == 2:
            result[parts[0]] = parts[1]
    return result

def read_old():
    if not REVIEWS.exists():
        return {}
    with REVIEWS.open(newline="") as stream:
        return {row["bundle_id"]: row for row in csv.DictReader(stream, delimiter="\t")}

def read_info(path):
    parser = ConfigParser(interpolation=None)
    parser.read(path / "activity" / "activity.info", encoding="utf-8")
    section = parser["Activity"]
    return section.get("bundle_id", path.name), section.get("name", path.name), section.get("activity_version", "")

def read_sugarizer(old):
    if not SUGARIZER_CATALOG.exists():
        return []
    revision = SUGARIZER_REVISION.read_text().strip()
    rows = []
    for activity in json.loads(SUGARIZER_CATALOG.read_text()):
        prior = old.get(activity["id"], {})
        rows.append({"bundle_id": activity["id"], "name": activity["name"],
            "version": str(activity.get("version", "")), "source_revision": revision,
            "source_path": f"packages/sugarizer/{activity['directory']}",
            "format": "sugarizer-web", "run_status": prior.get("run_status", "unreviewed"),
            "rating": prior.get("rating", ""), "notes": prior.get("notes", "catalog only; Sugarizer runtime not installed"),
            "last_tested": prior.get("last_tested", ""), "screenshot": prior.get("screenshot", "")})
    return rows

def main():
    old, revisions, rows = read_old(), read_revisions(), []
    for line in MANIFEST.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        source_name, _ = line.split("\t", 1)
        source = ROOT / "packages/upstream-activities" / source_name
        bundle_id, name, version = read_info(source)
        prior = old.get(bundle_id, {})
        rows.append({"bundle_id": bundle_id, "name": name, "version": version,
            "source_revision": revisions.get(source_name, ""),
            "source_path": str(source.relative_to(ROOT)), "format": "native-sugar-bundle",
            "run_status": prior.get("run_status", "unreviewed"), "rating": prior.get("rating", ""),
            "notes": prior.get("notes", ""), "last_tested": prior.get("last_tested", ""),
            "screenshot": prior.get("screenshot", "")})
    rows.extend(read_sugarizer(old))
    with REVIEWS.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"activity review inventory: {len(rows)} rows -> {REVIEWS}")

if __name__ == "__main__":
    main()
