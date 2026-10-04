#!/usr/bin/env python3
"""Check that the GTK4 lifecycle matrix matches the native activity catalog."""

from configparser import ConfigParser
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "scripts/sugar-gtk4-activity-matrix.sh"
PACKAGES = ROOT / "packages"

# These activities are supplied by pinned guest checkouts during the preview
# build, so their activity.info files are intentionally outside this repo.
GUEST_ONLY = {"org.laptop.ImageViewerActivity", "org.laptop.Log"}
ENTRY_RE = re.compile(r"^\s*'([^']+)\|([^']+)'\s*$")


def matrix_entries():
    entries = []
    for line in MATRIX.read_text(encoding="utf-8").splitlines():
        match = ENTRY_RE.match(line)
        if match:
            entries.append(match.groups())
    return entries


def native_entries():
    entries = {}
    for info in sorted(PACKAGES.glob("gtk4-*/activity/activity.info")):
        parser = ConfigParser(interpolation=None)
        parser.read(info, encoding="utf-8")
        activity = parser["Activity"]
        bundle_id = activity.get("bundle_id", "")
        command = activity.get("exec", "")
        assert bundle_id and command, info
        assert command.startswith("sugar-activity4 "), info
        entries[bundle_id] = command.removeprefix("sugar-activity4 ")
    return entries


def main():
    matrix = dict(matrix_entries())
    assert len(matrix) == 51, f"expected 51 matrix entries, found {len(matrix)}"
    assert len(matrix) == len(matrix_entries()), "duplicate matrix bundle ID"

    native = native_entries()
    missing = sorted(set(native) - set(matrix))
    unexpected = sorted(set(matrix) - set(native) - GUEST_ONLY)
    wrong_entrypoint = sorted(
        bundle for bundle in native.keys() & matrix.keys()
        if matrix[bundle] != native[bundle]
    )
    assert not missing, f"native bundles missing from matrix: {missing}"
    assert not unexpected, f"matrix bundles without a checked-in source: {unexpected}"
    assert not wrong_entrypoint, f"matrix entrypoint drift: {wrong_entrypoint}"
    assert set(matrix) - set(native) == GUEST_ONLY, "guest-only matrix set changed"
    print(f"gtk4 activity matrix: {len(matrix)} entries, {len(native)} native, PASS")


if __name__ == "__main__":
    main()
