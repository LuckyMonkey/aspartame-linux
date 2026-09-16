"""About my Computer must not claim the build is unknown.

The upstream probes are OLPC and Red Hat specific. On Aspartame they all miss,
so the build fell back to "Not available" even though /etc/os-release names
the image. Patch 0145 adds os-release as a source.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'patches/gtk4-preview/0145-aboutcomputer-build-from-os-release.patch'


def _added_lines():
    return [line[1:] for line in PATCH.read_text().splitlines()
            if line.startswith('+') and not line.startswith('+++')]


def test_patch_consults_os_release():
    added = '\n'.join(_added_lines())
    assert 'freedesktop_os_release' in added
    assert 'import platform' in added


def test_patch_prefers_the_image_identity_then_generic_names():
    added = '\n'.join(_added_lines())
    for key in ('IMAGE_ID', 'PRETTY_NAME', 'NAME'):
        assert key in added, key


def test_patch_still_falls_back_to_not_available():
    # An unidentifiable system must still say so rather than show nothing.
    assert '_not_available' in PATCH.read_text()


def test_patch_tolerates_a_missing_or_malformed_os_release():
    added = '\n'.join(_added_lines())
    assert 'except (OSError, ValueError)' in added


def test_build_routes_the_patch_to_the_shell_checkout():
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert '*0145*) target="$root/sources/sugar" ;;' in build
