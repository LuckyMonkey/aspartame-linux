import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).parents[1]
BRIDGE = ROOT / "scripts/sugar-chirality-space.sh"


def make_fake_switcher(tmp_path):
    log = tmp_path / "switcher.log"
    switcher = tmp_path / "switcher.sh"
    switcher.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' \"$1\" >> \"$SWITCHER_LOG\"\n"
    )
    switcher.chmod(0o755)
    return switcher, log


def run_bridge(tmp_path, switcher, *args):
    environment = os.environ.copy()
    environment["ASPARTAME_SPACE_SWITCHER"] = str(switcher)
    environment["SWITCHER_LOG"] = str(tmp_path / "switcher.log")
    return subprocess.run(
        [str(BRIDGE), *args],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def test_left_and_right_select_one_full_surface_each(tmp_path):
    switcher, log = make_fake_switcher(tmp_path)

    left = run_bridge(tmp_path, switcher, "left")
    right = run_bridge(tmp_path, switcher, "right")

    assert left.returncode == 0, left.stderr
    assert right.returncode == 0, right.stderr
    assert "mode=single-surface" in left.stdout
    assert "mode=single-surface" in right.stdout
    assert log.read_text().splitlines() == ["gtk3", "gtk4"]


def test_bridge_rejects_unknown_action_without_touching_spaces(tmp_path):
    switcher, log = make_fake_switcher(tmp_path)

    result = run_bridge(tmp_path, switcher, "compare")

    assert result.returncode == 2
    assert "usage:" in result.stderr
    assert not log.exists()


def test_iso_packages_the_semantic_model_and_cli_with_the_space_bridge():
    build = (ROOT / "scripts/build-iso.sh").read_text()
    assert "aspartame_chirality.py sugar-chirality.py" in build
    assert "sugar-chirality-space.sh" in build
