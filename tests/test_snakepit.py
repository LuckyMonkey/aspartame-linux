import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).parents[1]
SNAKEPIT = ROOT / "scripts/snakepit.py"
BUILD_ISO = ROOT / "scripts/build-iso.sh"
PACKAGED_WRAPPER = ROOT / "archiso/aspartame/airootfs/usr/local/bin/aspartame-snakepit"


def test_snakepit_qualifies_an_isolated_python_workflow(tmp_path):
    source = tmp_path / "specimen"
    source.mkdir()
    (source / "requirements.txt").write_text("# standard-library specimen\n")
    (source / "pyproject.toml").write_text(
        "[project]\n"
        "name = 'snakepit-specimen'\n"
        "requires-python = '>=3.8,<4'\n"
    )
    (source / "probe.py").write_text(
        "import os, sys\n"
        "assert sys.prefix != sys.base_prefix\n"
        "assert os.environ['PYTHONNOUSERSITE'] == '1'\n"
        "print('workflow-ok')\n"
    )
    environment = tmp_path / "venv"
    record = tmp_path / "qualification.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SNAKEPIT),
            "qualify",
            "--software",
            "specimen",
            "--source",
            str(source),
            "--environment",
            str(environment),
            "--record",
            str(record),
            "--command",
            "python",
            "-m",
            "probe",
        ],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    data = json.loads(record.read_text())
    assert data["schema"] == "aspartame.snakepit.qualification/v0"
    assert data["status"] == "PASS"
    assert data["requirements"]["files"][0]["entries"] == []
    assert data["compatibility"]["satisfied"] is True
    assert data["steps"][0]["action"] == "check-interpreter"
    assert data["environment"]["isolation"]["isolated"] is True
    assert data["workflow"]["command"][0] == str(environment / "bin" / "python")
    assert "workflow-ok" in data["workflow"]["stdout"]


def test_snakepit_launches_an_explicit_qualified_contract(tmp_path):
    source = tmp_path / "launchable"
    source.mkdir()
    (source / "pyproject.toml").write_text(
        "[project]\n"
        "name = 'launchable-specimen'\n"
        "requires-python = '>=3.8,<4'\n"
    )
    (source / "probe.py").write_text(
        "import os, sys\n"
        "assert sys.prefix != sys.base_prefix\n"
        "assert os.environ['ASPARTAME_SNAKEPIT_ENVIRONMENT']\n"
        "print('launch-workflow-ok')\n"
    )
    environment = tmp_path / "venv"
    record = tmp_path / "qualification.json"

    qualify = subprocess.run(
        [
            sys.executable,
            str(SNAKEPIT),
            "qualify",
            "--software",
            "launchable-specimen",
            "--source",
            str(source),
            "--environment",
            str(environment),
            "--record",
            str(record),
            "--launchable",
            "--command",
            "python",
            "-m",
            "probe",
        ],
        text=True,
        capture_output=True,
    )

    assert qualify.returncode == 0, qualify.stderr
    data = json.loads(record.read_text())
    assert data["launch"]["command"] == data["workflow"]["command"]
    assert data["launch"]["cwd"] == str(source)

    launched = subprocess.run(
        [sys.executable, str(SNAKEPIT), "launch", "--record", str(record)],
        text=True,
        capture_output=True,
    )

    assert launched.returncode == 0, launched.stderr
    assert "launch=PASS software=launchable-specimen" in launched.stdout
    assert "launch-workflow-ok" in launched.stdout


def test_snakepit_records_candidates_and_skips_unavailable_interpreters(tmp_path):
    source = tmp_path / "specimen"
    source.mkdir()
    (source / "pyproject.toml").write_text(
        "[project]\n"
        "name = 'candidate-specimen'\n"
        "requires-python = '>=3.8,<4'\n"
    )
    environment = tmp_path / "venv"
    record = tmp_path / "qualification.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SNAKEPIT),
            "qualify",
            "--software",
            "candidate-specimen",
            "--source",
            str(source),
            "--environment",
            str(environment),
            "--record",
            str(record),
            "--python",
            "python-that-is-not-installed",
            "--python",
            sys.executable,
            "--command",
            "python",
            "-c",
            "import sys; assert sys.prefix != sys.base_prefix",
        ],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    data = json.loads(record.read_text())
    candidates = data["interpreter"]["candidates"]
    assert candidates[0]["requested"] == "python-that-is-not-installed"
    assert "error" in candidates[0]
    assert candidates[1]["resolved"] == str(Path(sys.executable).resolve())
    assert data["interpreter"]["requested"] == str(Path(sys.executable).resolve())
    assert data["steps"][0]["candidates"] == candidates


def test_snakepit_refuses_to_reuse_an_environment_without_explicit_flag(tmp_path):
    source = tmp_path / "specimen"
    source.mkdir()
    environment = tmp_path / "venv"
    environment.mkdir()

    result = subprocess.run(
        [
            sys.executable,
            str(SNAKEPIT),
            "qualify",
            "--software",
            "specimen",
            "--source",
            str(source),
            "--environment",
            str(environment),
            "--record",
            str(tmp_path / "refused.json"),
            "--command",
            "python",
            "-c",
            "print('not-run')",
        ],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "use a new path or --reuse" in result.stderr


def test_snakepit_records_an_interpreter_capability_gap(tmp_path):
    source = tmp_path / "specimen"
    source.mkdir()
    (source / "pyproject.toml").write_text(
        "[project]\n"
        "name = 'future-specimen'\n"
        "requires-python = '>=99'\n"
    )
    environment = tmp_path / "venv"
    record = tmp_path / "incompatible.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SNAKEPIT),
            "qualify",
            "--software",
            "future-specimen",
            "--source",
            str(source),
            "--environment",
            str(environment),
            "--record",
            str(record),
            "--command",
            "python",
            "-c",
            "print('must-not-run')",
        ],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "does not satisfy requires-python" in result.stderr
    data = json.loads(record.read_text())
    assert data["status"] == "FAIL"
    assert data["compatibility"]["satisfied"] is False
    assert data["workflow"] == {}
    assert not environment.exists()


def test_snakepit_rejects_dependency_tension_before_environment_creation(tmp_path):
    source = ROOT / "tests/fixtures/snakepit/dependency-tension"
    environment = tmp_path / "venv"
    record = tmp_path / "dependency-tension.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SNAKEPIT),
            "qualify",
            "--software",
            "dependency-tension-specimen",
            "--source",
            str(source),
            "--environment",
            str(environment),
            "--record",
            str(record),
            "--command",
            "python",
            "-m",
            "probe",
        ],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "dependency conflict before environment creation" in result.stderr
    data = json.loads(record.read_text())
    assert data["status"] == "FAIL"
    assert data["requirements"]["dependency_conflicts"][0]["name"] == (
        "aspartame-tension-core"
    )
    assert data["steps"][1]["action"] == "check-dependencies"
    assert data["steps"][1]["status"] == "conflict"
    assert data["workflow"] == {}
    assert not environment.exists()


def test_snakepit_qualifies_two_isolated_dependency_versions(tmp_path):
    fixture_root = ROOT / "tests/fixtures/snakepit/dependency-pair"
    cases = {
        "left": ("1.0.0", "shared-v1"),
        "right": ("2.0.0", "shared-v2"),
    }

    for side, (version, source_name) in cases.items():
        source = fixture_root / f"app-{side}"
        record = tmp_path / f"{side}.json"
        environment = tmp_path / side
        result = subprocess.run(
            [
                sys.executable,
                str(SNAKEPIT),
                "qualify",
                "--software",
                f"dependency-pair-{side}",
                "--source",
                str(source),
                "--environment",
                str(environment),
                "--record",
                str(record),
                "--install-requirements",
                "--command",
                "python",
                "-m",
                "probe",
            ],
            text=True,
            capture_output=True,
        )

        assert result.returncode == 0, result.stderr
        data = json.loads(record.read_text())
        assert data["status"] == "PASS"
        assert data["requirements"]["dependency_conflicts"] == []
        assert data["steps"][1]["action"] == "check-dependencies"
        assert data["steps"][2]["action"] == "create-venv"
        assert data["steps"][3]["action"] == "install-requirements"
        assert data["steps"][3]["returncode"] == 0
        assert f"tension-core={version}" in data["workflow"]["stdout"]
        assert data["environment"]["isolation"]["isolated"] is True
        assert source_name in data["requirements"]["files"][0]["entries"][0]


def test_snakepit_is_staged_in_the_standalone_image():
    build = BUILD_ISO.read_text()
    wrapper = PACKAGED_WRAPPER.read_text()
    assert 'scripts/snakepit.py' in build
    assert 'usr/share/aspartame/snakepit.py' in build
    assert 'exec /usr/bin/python3 /usr/share/aspartame/snakepit.py "$@"' in wrapper
