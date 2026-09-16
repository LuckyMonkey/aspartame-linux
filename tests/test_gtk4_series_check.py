"""The series check must mirror the build's routing and fail closed.

sugar-gtk4-build.sh runs against a checkout that earlier runs already
mutated and accepts a patch that merely reverse-applies, so it can report
success while the series no longer reconstructs the preview from its pinned
baseline. sugar-gtk4-series-check.sh answers that separate question, and is
only useful while its routing agrees with the build's.
"""

import fnmatch
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts/sugar-gtk4-build.sh"
CHECK = ROOT / "scripts/sugar-gtk4-series-check.sh"
PATCH_DIR = ROOT / "patches/gtk4-preview"

TARGET_NAMES = {
    "$toolkit": "sugar-toolkit-gtk4",
    "$ext": "sugar-ext",
    "$log_activity": "log-activity",
    "$root/sources/sugar": "sugar",
    "$root/sources/sugar-datastore": "sugar-datastore",
    "$casilda": "casilda",
}


def _build_routing():
    lines = BUILD.read_text().splitlines()
    start = next(i for i, l in enumerate(lines)
                 if l.strip().startswith('case "$patch" in'))
    end = next(i for i, l in enumerate(lines[start:], start)
               if l.strip() == "esac")
    rules = []
    for line in lines[start + 1:end]:
        match = re.match(r'\s*(\S.*?)\)\s*(?:target="([^"]+)"|echo)', line)
        if match:
            rules.append(([p.strip() for p in match.group(1).split("|")],
                          match.group(2)))
    return rules


def _build_target(path):
    for patterns, target in _build_routing():
        if any(fnmatch.fnmatch(str(path), pattern) for pattern in patterns):
            return TARGET_NAMES.get(target, "SKIP" if target is None else target)
    return None


def _check_target(path):
    script = (
        'source <(sed -n "/^route()/,/^}/p" '
        f'{CHECK}); route "{path}"'
    )
    done = subprocess.run(["bash", "-c", script],
                          capture_output=True, text=True)
    return done.stdout.strip()


def test_series_check_is_executable_and_parses():
    assert CHECK.exists()
    subprocess.run(["bash", "-n", str(CHECK)], check=True)


def test_series_check_routing_matches_the_build():
    mismatched = []
    for patch in sorted(PATCH_DIR.glob("*.patch")):
        want, got = _build_target(patch), _check_target(patch)
        if want != got:
            mismatched.append((patch.name, want, got))
    assert mismatched == [], mismatched


def test_series_check_starts_from_the_pinned_baseline():
    text = CHECK.read_text()
    # It must build its tree from the committed SHA, not from the working
    # checkout the previous build already modified.
    assert "git -C \"$src\" archive HEAD" in text
    assert "GTK4_ROOT" in text


def test_series_check_fails_when_a_rebuild_would_not_import():
    text = CHECK.read_text()
    assert "py_compile" in text
    assert "Result: FAIL (a clean rebuild would not import)" in text
    assert "exit 1" in text


def test_make_exposes_the_series_check():
    makefile = (ROOT / "Makefile").read_text()
    assert "sugar-gtk4-series-check:" in makefile
    assert "./scripts/sugar-gtk4-series-check.sh" in makefile
