"""Exercise the actual shell wrapper, including argument forwarding."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_wrapper_calls_console_entrypoint_and_preserves_arguments(tmp_path):
    package = tmp_path / "sugar4" / "activity"
    package.mkdir(parents=True)
    (package.parent / "__init__.py").touch()
    (package / "__init__.py").touch()
    (package / "activityinstance.py").write_text(
        "import sys\ndef main():\n"
        "    print(repr(sys.argv[1:]))\n"
        "    raise SystemExit(23)\n"
    )
    arguments = ["/some/Activity with spaces", "logviewer.LogActivity", "-a", "test-id"]
    result = subprocess.run(
        [str(ROOT / "scripts/sugar-activity4"), *arguments],
        env={**os.environ, "PYTHON_BIN": sys.executable, "PYTHONPATH": str(tmp_path)},
        capture_output=True, text=True,
    )
    assert result.returncode == 23, result.stderr
    assert result.stdout.strip() == repr(arguments)
