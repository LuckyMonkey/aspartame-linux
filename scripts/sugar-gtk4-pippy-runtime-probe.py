#!/usr/bin/env python3
"""Run the native Pippy execution boundary inside the GTK4 guest runtime."""

from pathlib import Path
import sys
import threading
import time


PACKAGE = Path("/mnt/aspartame-dev/packages/gtk4-pippy-activity")
if PACKAGE.is_dir():
    sys.path.insert(0, str(PACKAGE))

from pippy_runner import run_program, runtime_descriptor


def main():
    runtime = runtime_descriptor()
    assert runtime["isolated"]
    assert runtime["user_site"] == "disabled"
    assert runtime["working_directory"] == "disposable temporary directory"
    assert runtime["network"] == "not sandboxed"
    assert runtime["resource_limits"]["cpu_seconds"] == 2
    assert runtime["io_limits"]["output_bytes"] == 64 * 1024
    output = run_program("print('pippy-runtime-ok')", timeout=2)
    assert output.returncode == 0
    assert output.output.strip() == "pippy-runtime-ok"
    error = run_program("raise RuntimeError('bounded-error')", timeout=2)
    assert error.returncode != 0
    assert "RuntimeError: bounded-error" in error.output
    timeout = run_program("while True: pass", timeout=0.2)
    assert timeout.timed_out
    cancel = threading.Event()
    threading.Thread(
        target=lambda: (time.sleep(0.1), cancel.set()), daemon=True
    ).start()
    cancelled = run_program("while True: pass", timeout=2, cancel_event=cancel)
    assert cancelled.cancelled
    noisy = run_program("print('x' * 200000)", timeout=2)
    assert noisy.output_truncated
    print(
        "pippy-runtime=PASS output=PASS error=PASS "
        "wall-timeout=PASS cancel=PASS isolated-runner=PASS "
        "runtime-contract=PASS",
        flush=True,
    )


if __name__ == "__main__":
    main()
