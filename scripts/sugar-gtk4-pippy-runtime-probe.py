#!/usr/bin/env python3
"""Run the native Pippy execution boundary inside the GTK4 guest runtime."""

from pathlib import Path
import sys
import threading
import time


PACKAGE = Path("/mnt/aspartame-dev/packages/gtk4-pippy-activity")
if PACKAGE.is_dir():
    sys.path.insert(0, str(PACKAGE))

from pippy_runner import run_program


def main():
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
    print(
        "pippy-runtime=PASS output=PASS error=PASS "
        "wall-timeout=PASS cancel=PASS isolated-runner=PASS",
        flush=True,
    )


if __name__ == "__main__":
    main()
