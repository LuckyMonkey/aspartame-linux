#!/usr/bin/env python3
"""Side-by-side GTK3 (F7) vs GTK4 (F8) Activity parity workflow.

Subcommands:

  pairs            Rewrite docs/sugar-modernization/parity/PAIRS.tsv: every GTK4
                   Activity, its GTK3 reference, and its current port class.
  new BUNDLE_ID    Start a comparison report in reports/gtk4/parity/ from the
                   template, prefilled for that Activity.
  export           Score every report and rewrite the Activity Manager's
                   gtk4-overlay/src/cpsection/activities/port_status.json.
  check            Exit non-zero if PAIRS.tsv or port_status.json is stale.

A report's steps are scored on the Wong-Baker-style scale used by the Activity
Manager (0 = no hurt .. 10 = unusable).  A report's score is its *worst*
scored step, and a report with any unscored step counts as in progress, so a
single good step never hides a bad one.  The newest report per Activity wins.

This is F7/F8 machinery for the GTK3->GTK4 migration.  When Chirality takes
over the Spaces (see ASPARTAME_CHIRALITY.md), the reports and scores remain
valid evidence; only the "open it in F7, then F8" instructions change.
"""

import argparse
import configparser
import csv
import datetime
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAIRS = ROOT / "docs/sugar-modernization/parity/PAIRS.tsv"
TEMPLATE = ROOT / "docs/sugar-modernization/parity/TEMPLATE.md"
REPORTS = ROOT / "reports/gtk4/parity"
CLASSIFICATION = ROOT / "docs/sugar-modernization/ACTIVITY_PORT_CLASSIFICATION.md"
REVIEWS = ROOT / "docs/activity-reviews/REVIEWS.tsv"
STATUS = ROOT / "gtk4-overlay/src/cpsection/activities/port_status.json"
SCORES = (0, 2, 4, 6, 8, 10)
CLASSES = ("FULL PORT", "FUNCTIONAL PORT", "COVERAGE IMPLEMENTATION", "PLACEHOLDER")

# GTK3 references that come from Arch packages rather than pinned sources.
ARCH_REFERENCES = {
    "org.laptop.WebActivity": "sugar-activity-browse",
    "org.aspartame.Calculate": "sugar-activity-calculate",
    "org.laptop.ImageViewerActivity": "sugar-activity-imageviewer",
    "org.laptop.sugar.Jukebox": "sugar-activity-jukebox",
    "org.sugarlabs.Paint": "sugar-activity-paint",
    "org.laptop.Pippy": "sugar-activity-pippy",
    "org.laptop.sugar.ReadActivity": "sugar-activity-read",
    "org.laptop.RecordActivity": "sugar-activity-record",
    "org.laptop.Terminal": "sugar-activity-terminal",
    "org.sugarlabs.Write": "sugar-activity-write",
    "org.aspartame.Count": "packages/aspartame-count/Count.activity",
}
# GTK4 Activities built from pinned upstream sources, not packages/gtk4-*.
PINNED_GTK4 = (
    ("org.laptop.ImageViewerActivity", "Image Viewer", "pinned:imageviewer-activity"),
    ("org.laptop.Log", "Log", "pinned:log-activity"),
)
HEADER = ("bundle_id", "name", "gtk3_reference", "gtk4_source", "port_class")


def _key(name):
    return re.sub(r"[^a-z0-9]", "", name.casefold())


def classifications():
    found = {}
    for line in CLASSIFICATION.read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[1] in CLASSES:
            found[_key(cells[0])] = cells[1]
    return found


def review_sources():
    sources = {}
    with REVIEWS.open(encoding="utf-8") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            if row.get("format") == "native-sugar-bundle" and row.get("source_path"):
                sources[row["bundle_id"]] = row["source_path"]
            elif row.get("format") == "sugarizer-web" and row.get("source_path"):
                # No GTK3 bundle exists; compare against the web Activity.
                sources.setdefault(row["bundle_id"], "sugarizer-web:" + row["source_path"])
    # Pinned upstream GTK3 sources are authoritative even without a review row.
    for info_path in sorted(ROOT.glob("packages/upstream-activities/*/activity/activity.info")):
        info = configparser.ConfigParser(strict=False, interpolation=None)
        try:
            info.read(info_path, encoding="utf-8")
            bundle_id = info["Activity"]["bundle_id"].strip()
        except (configparser.Error, KeyError, UnicodeError):
            continue
        sources.setdefault(bundle_id, str(info_path.parents[1].relative_to(ROOT)))
    return sources


def build_pairs():
    classes, sources, rows = classifications(), review_sources(), []
    entries = []
    for info_path in sorted(ROOT.glob("packages/gtk4-*-activity/activity/activity.info")):
        info = configparser.ConfigParser()
        info.read(info_path, encoding="utf-8")
        activity = info["Activity"]
        entries.append((activity["bundle_id"].strip(), activity["name"].strip(),
                        str(info_path.parents[1].relative_to(ROOT))))
    entries.extend(PINNED_GTK4)
    for bundle_id, name, gtk4_source in sorted(entries, key=lambda e: e[1].casefold()):
        reference = sources.get(bundle_id) or ARCH_REFERENCES.get(bundle_id) or "none recorded"
        rows.append((bundle_id, name, reference, gtk4_source,
                     classes.get(_key(name), "UNCLASSIFIED")))
    return rows


def render_pairs(rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter="\t", lineterminator="\n")
    writer.writerow(HEADER)
    writer.writerows(rows)
    return buffer.getvalue()


def read_pairs():
    with PAIRS.open(encoding="utf-8") as stream:
        return {row["bundle_id"]: row for row in csv.DictReader(stream, delimiter="\t")}


STEP_ROW = re.compile(r"^\|\s*S\d+\s*\|")
META = re.compile(r"^- \*\*(?P<key>[A-Za-z ]+):\*\*\s*(?P<value>.*)$")


def parse_report(path):
    """Return metadata and step scores; score is None if any step is unscored."""
    meta, steps = {}, []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = META.match(line.strip())
        if match:
            meta[match["key"].strip().lower()] = match["value"].strip().strip("`")
        if STEP_ROW.match(line.strip()):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            value = cells[-1]
            steps.append(int(value) if value.isdigit() and int(value) in SCORES else None)
    scored = [s for s in steps if s is not None]
    complete = bool(steps) and len(scored) == len(steps)
    return {
        "bundle_id": meta.get("bundle id", ""),
        "date": meta.get("date", ""),
        "score": max(scored) if complete else None,
        "steps": len(steps),
        "scored": len(scored),
    }


def build_status():
    pairs = read_pairs()
    status = {bundle_id: {"name": row["name"], "class": row["port_class"], "parity": None}
              for bundle_id, row in pairs.items()}
    for path in sorted(REPORTS.glob("*.md")) if REPORTS.is_dir() else ():
        report = parse_report(path)
        entry = status.get(report["bundle_id"])
        if entry is None:
            continue
        current = entry["parity"]
        if current is None or report["date"] >= current["date"]:
            entry["parity"] = {
                "date": report["date"],
                "report": str(path.relative_to(ROOT)),
                "score": report["score"],
                "progress": "%d/%d steps scored" % (report["scored"], report["steps"]),
            }
    return status


def render_status(status):
    return json.dumps({"version": 1, "activities": status}, indent=1, sort_keys=True) + "\n"


def cmd_pairs(_args):
    PAIRS.parent.mkdir(parents=True, exist_ok=True)
    PAIRS.write_text(render_pairs(build_pairs()), encoding="utf-8")
    print("wrote %s" % PAIRS.relative_to(ROOT))


def cmd_new(args):
    pairs = read_pairs()
    if args.bundle_id not in pairs:
        raise SystemExit("unknown bundle id %r; run `pairs` or see PAIRS.tsv" % args.bundle_id)
    row = pairs[args.bundle_id]
    date = args.date or datetime.date.today().isoformat()
    slug = _key(row["name"]) or "activity"
    target = REPORTS / ("%s-%s.md" % (slug, date.replace("-", "")))
    if target.exists():
        raise SystemExit("%s already exists; edit it instead" % target.relative_to(ROOT))
    text = TEMPLATE.read_text(encoding="utf-8")
    for field, value in (("NAME", row["name"]), ("BUNDLE_ID", row["bundle_id"]),
                         ("DATE", date), ("GTK3", row["gtk3_reference"]),
                         ("GTK4", row["gtk4_source"]), ("CLASS", row["port_class"])):
        text = text.replace("{{%s}}" % field, value)
    REPORTS.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    print(target.relative_to(ROOT))


def cmd_export(_args):
    STATUS.write_text(render_status(build_status()), encoding="utf-8")
    print("wrote %s" % STATUS.relative_to(ROOT))


def cmd_check(_args):
    stale = []
    if not PAIRS.exists() or PAIRS.read_text(encoding="utf-8") != render_pairs(build_pairs()):
        stale.append("%s (run: scripts/sugar-parity.py pairs)" % PAIRS.relative_to(ROOT))
    elif not STATUS.exists() or STATUS.read_text(encoding="utf-8") != render_status(build_status()):
        stale.append("%s (run: scripts/sugar-parity.py export)" % STATUS.relative_to(ROOT))
    if stale:
        print("parity data is stale:\n  " + "\n  ".join(stale), file=sys.stderr)
        return 1
    print("parity-check=PASS")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("pairs").set_defaults(func=cmd_pairs)
    new = commands.add_parser("new")
    new.add_argument("bundle_id")
    new.add_argument("--date", help="YYYY-MM-DD (default: today)")
    new.set_defaults(func=cmd_new)
    commands.add_parser("export").set_defaults(func=cmd_export)
    commands.add_parser("check").set_defaults(func=cmd_check)
    args = parser.parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
