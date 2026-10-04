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


@dataclass(frozen=True)
class RunResult:
    output: str
    returncode: int
    timed_out: bool = False
    cancelled: bool = False


def _combined_output(stdout: str, stderr: str) -> str:
    if stdout and stderr:
        return f"{stdout}\n{stderr}"
    return stdout or stderr


def run_program(program: str, *, timeout: float = 5.0,
                input_text: str = "", cancel_event=None) -> RunResult:
    """Run one source buffer in a bounded, disposable working directory."""

    with tempfile.TemporaryDirectory(prefix="aspartame-pippy-") as directory:
        Path(directory, "program.py").write_text(program, encoding="utf-8")
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
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
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
            output = _combined_output(stdout, stderr)
            detail = f"Program timed out after {timeout:g} seconds."
            if output:
                detail = f"{output}\n{detail}"
            return RunResult(
                detail,
                process.returncode if process.returncode is not None else 1,
                timed_out=True,
            )
        finally:
            if cancel_watcher is not None:
                cancel_watcher.join(timeout=0.5)
        output = _combined_output(stdout, stderr)
        cancelled = cancel_event is not None and cancel_event.is_set()
        return RunResult(
            output,
            process.returncode if process.returncode is not None else 1,
            cancelled=cancelled,
        )
