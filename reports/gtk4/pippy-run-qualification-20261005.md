# GTK4 Pippy Run integration — 2026-10-05

The bounded Python runner was already qualified independently. This pass
qualifies the user-facing GTK4 handoff:

1. resume a Journal object containing `print("Aspartame")`;
2. activate the visible Run action through AT-SPI;
3. wait for the runner to finish;
4. verify `Aspartame` in the accessible Output view and `Finished` status;
5. save, stop, and release the Activity cleanly.

The [headless completed-run capture](pippy-run-20261005.png) was taken with:

```text
SSH_PORT=2230 ./scripts/ssh-asp \
  '/usr/lib/aspartame/gtk4-preview/venv/bin/python /mnt/aspartame-dev/scripts/sugar-gtk4-pippy-roundtrip.py 1 /tmp/pippy-run-20261005.png'
```

Receipt:

```text
cycle=1 ... resume=PASS service-release=PASS shell-cleanup=PASS
pippy-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

This advances the Python runtime path without claiming a security sandbox,
network isolation, or full upstream Pippy feature parity.
