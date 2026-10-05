"""Bounded local execution for the native GTK4 Pippy Activity.

This is an execution boundary, not a security sandbox.  It isolates the
working directory, disables user-site loading, applies conservative POSIX
resource limits in the child, and kills the complete process group on a wall
clock timeout.  A future stronger sandbox can replace this module without
changing the Activity UI contract.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
import platform
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading


BOOTSTRAP = """
import resource
import runpy

limits = (
    (resource.RLIMIT_CPU, 2, 2),
    # The preview's Python 3.14 zipimport/runtime mappings exceed 256 MiB
    # before user code starts; keep a bounded 1 GiB ceiling instead.
    (resource.RLIMIT_AS, 1024 * 1024 * 1024, 1024 * 1024 * 1024),
    (resource.RLIMIT_FSIZE, 1 * 1024 * 1024, 1 * 1024 * 1024),
    (resource.RLIMIT_NOFILE, 32, 32),
)
for kind, soft, hard in limits:
    try:
        resource.setrlimit(kind, (soft, hard))
    except (ValueError, OSError):
        pass
runpy.run_path("program.py", run_name="__main__")
"""


RESOURCE_LIMITS = {
    "cpu_seconds": 2,
    "address_space_bytes": 1024 * 1024 * 1024,
    "file_size_bytes": 1 * 1024 * 1024,
    "open_files": 32,
}

IO_LIMITS = {
    "source_bytes": 256 * 1024,
    "input_bytes": 64 * 1024,
    "output_bytes": 64 * 1024,
}


@dataclass(frozen=True)
class RunResult:
    output: str
    returncode: int
    timed_out: bool = False
    cancelled: bool = False
    output_truncated: bool = False


def runtime_descriptor():
    """Describe the child runtime contract without claiming a sandbox."""

    return {
        "implementation": platform.python_implementation(),
        "version": platform.python_version(),
        "interpreter": sys.executable,
        "isolated": True,
        "user_site": "disabled",
        "working_directory": "disposable temporary directory",
        "network": "not sandboxed",
        "resource_limits": dict(RESOURCE_LIMITS),
        "io_limits": dict(IO_LIMITS),
    }


def _read_bounded(path: Path) -> tuple[str, bool]:
    data = path.read_bytes()
    truncated = len(data) > IO_LIMITS["output_bytes"]
    if truncated:
        data = data[:IO_LIMITS["output_bytes"]]
    return data.decode("utf-8", errors="replace"), truncated


def _combined_output(stdout: str, stderr: str) -> str:
    if stdout and stderr:
        return f"{stdout}\n{stderr}"
    return stdout or stderr


def run_program(program: str, *, timeout: float = 5.0,
                input_text: str = "", cancel_event=None) -> RunResult:
    """Run one source buffer in a bounded, disposable working directory."""

    source_bytes = program.encode("utf-8")
    input_bytes = input_text.encode("utf-8")
    if len(source_bytes) > IO_LIMITS["source_bytes"]:
        return RunResult("Program is too large to run in Pippy.", 1)
    if len(input_bytes) > IO_LIMITS["input_bytes"]:
        return RunResult("Program input is too large to run in Pippy.", 1)

    with tempfile.TemporaryDirectory(prefix="aspartame-pippy-") as directory:
        Path(directory, "program.py").write_text(program, encoding="utf-8")
        stdout_path = Path(directory, "stdout.txt")
        stderr_path = Path(directory, "stderr.txt")
        stdout_file = stdout_path.open("wb")
        stderr_file = stderr_path.open("wb")
        environment = {
            "HOME": directory,
            "PATH": os.defpath,
            "PYTHONIOENCODING": "utf-8",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "TMPDIR": directory,
        }
        process = subprocess.Popen(
            [sys.executable, "-I", "-c", BOOTSTRAP],
            cwd=directory,
            env=environment,
            stdin=subprocess.PIPE,
            stdout=stdout_file,
            stderr=stderr_file,
            text=True,
            start_new_session=True,
        )
        cancel_watcher = None
        if cancel_event is not None:
            def watch_cancel():
                while process.poll() is None:
                    if cancel_event.wait(0.05):
                        if process.poll() is None:
                            try:
                                os.killpg(process.pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                        return

            cancel_watcher = threading.Thread(target=watch_cancel, daemon=True)
            cancel_watcher.start()
        try:
            stdout, stderr = process.communicate(input=input_text, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            stdout_file.close(); stderr_file.close()
            stdout, stdout_truncated = _read_bounded(stdout_path)
            stderr, stderr_truncated = _read_bounded(stderr_path)
            output = _combined_output(stdout, stderr)
            output_truncated = stdout_truncated or stderr_truncated
            detail = f"Program timed out after {timeout:g} seconds."
            if output:
                detail = f"{output}\n{detail}"
            if output_truncated:
                detail = f"{detail}\nOutput was truncated at {IO_LIMITS['output_bytes']} bytes."
            return RunResult(
                detail,
                process.returncode if process.returncode is not None else 1,
                timed_out=True,
                output_truncated=output_truncated,
            )
        finally:
            if cancel_watcher is not None:
                cancel_watcher.join(timeout=0.5)
        stdout_file.close(); stderr_file.close()
        stdout, stdout_truncated = _read_bounded(stdout_path)
        stderr, stderr_truncated = _read_bounded(stderr_path)
        output = _combined_output(stdout, stderr)
        output_truncated = stdout_truncated or stderr_truncated
        if output_truncated:
            output = f"{output}\nOutput was truncated at {IO_LIMITS['output_bytes']} bytes."
        cancelled = cancel_event is not None and cancel_event.is_set()
        return RunResult(
            output,
            process.returncode if process.returncode is not None else 1,
            cancelled=cancelled,
            output_truncated=output_truncated,
        )
