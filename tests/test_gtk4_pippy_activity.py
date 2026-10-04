import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).parents[1]
RUNNER = ROOT / "packages/gtk4-pippy-activity/pippy_runner.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("pippy_runner_test", RUNNER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_pippy_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-pippy-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "pippyactivity4.py").read_text()
    assert "bundle_id = org.laptop.Pippy" in info
    assert "sugar-activity4 pippyactivity4.PippyActivity" in info
    assert "class PippyActivity(SimpleActivity)" in source
    assert 'label="Run"' in source and 'label="Stop"' in source and "Program output" in source
    assert 'OUTPUT_PLACEHOLDER = "Run the program to see output."' in source
    assert "from pippy_runner import run_program" in source
    assert "run_program(" in source and "cancel_event=cancel_event" in source
    assert "_run_generation" in source
    assert "cancel_event" in source and "_stop_program" in source
    assert "editor_frame" in source and "output_frame" in source
    assert "Gtk.Frame(label=\"Python program\")" in source
    assert "Gtk.Grid" in source and "set_column_homogeneous(True)" in source
    assert "root.append(panes)" in source
    assert "frame.code-pane" in source
    assert "EXAMPLES = {" in source and "Program input" in source
    assert "_editor_key" in source and "_goto_line" in source
    matrix = (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "org.laptop.Pippy|pippyactivity4.PippyActivity" in matrix
    for script in ("sugar-gtk4-dev-sync.sh", "sugar-gtk4-build.sh"):
        assert "gtk4-pippy-activity" in (ROOT / "scripts" / script).read_text()


def test_pippy_journal_roundtrip_is_utf8():
    source = (ROOT / "packages/gtk4-pippy-activity/pippyactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert 'encoding="utf-8"' in source


def test_pippy_runner_executes_source_with_captured_output():
    runner = load_runner()
    result = runner.run_program("print('runner-ok')", timeout=2)
    assert result.returncode == 0
    assert result.output.strip() == "runner-ok"
    assert not result.timed_out


def test_pippy_runner_passes_program_input():
    runner = load_runner()
    result = runner.run_program(
        "value = input(); print(value.upper())",
        input_text="sugar\n",
        timeout=2,
    )
    assert result.returncode == 0
    assert result.output.strip() == "SUGAR"


def test_pippy_runner_reports_errors_and_kills_wall_clock_timeout():
    runner = load_runner()
    error = runner.run_program("raise ValueError('expected')", timeout=2)
    assert error.returncode != 0
    assert "ValueError: expected" in error.output

    timeout = runner.run_program("import time; time.sleep(10)", timeout=0.1)
    assert timeout.timed_out
    assert "timed out" in timeout.output


def test_pippy_runner_cancels_the_child_process_group():
    import threading

    runner = load_runner()
    cancel = threading.Event()
    threading.Timer(0.1, cancel.set).start()
    result = runner.run_program("while True: pass", timeout=2, cancel_event=cancel)
    assert result.cancelled
    assert not result.timed_out


def test_guest_pippy_runtime_probe_exercises_output_error_and_timeout():
    probe = (ROOT / "scripts/sugar-gtk4-pippy-runtime-probe.py").read_text()
    assert "from pippy_runner import run_program" in probe
    assert '"pippy-runtime-ok"' in probe
    assert "wall-timeout=PASS" in probe
    assert "cancel_event=cancel" in probe
    assert "cancel=PASS" in probe
