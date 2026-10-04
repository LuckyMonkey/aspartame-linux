# GTK4 Pippy Python runtime boundary - 2026-10-04

Scope: make the native Pippy Run action bounded and deterministic while
preserving the simple offline learning workflow.

Changes:

- `pippy_runner.py` writes each source buffer to a disposable working
  directory and invokes the selected GTK4 runtime in isolated mode;
- the child receives conservative CPU, address-space, file-size, and open-file
  limits;
- the complete process group is killed on wall-clock timeout;
- the Activity disables Run during execution and ignores stale results after
  Reset or a newer Run;
- output, traceback/error, and timeout states remain visible in the Output
  pane.

Guest probe:

```sh
SSH_PORT=2230 ./scripts/ssh-asp \
  /usr/lib/aspartame/gtk4-preview/venv/bin/python \
  /mnt/aspartame-dev/scripts/sugar-gtk4-pippy-runtime-probe.py
```

Result:

```text
pippy-runtime=PASS output=PASS error=PASS wall-timeout=PASS isolated-runner=PASS
```

This is bounded local execution, not a security sandbox. The next runtime
boundary for stronger isolation would need an explicit OS sandbox policy; no
claim of network denial or full upstream Pippy feature parity is made here.
