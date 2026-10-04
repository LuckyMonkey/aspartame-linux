# GTK4 Chirality crash isolation - 2026-10-04

Scope: verify that an exited or crashed held Activity cannot destroy the
other semantic hand or leave stale active state.

Probe:

```sh
SSH_PORT=2230 ./scripts/ssh-asp \
  /usr/lib/aspartame/gtk4-preview/venv/bin/python \
  /mnt/aspartame-dev/scripts/sugar-gtk4-chirality-crash-roundtrip.py
```

Result:

```text
chirality-crash-roundtrip=PASS crashed=right preserved=left active=left state-clean=PASS mode=single-surface
```

The probe launches Calculate and Clock, assigns them to Left and Right, then
terminates the held Right process with `SIGKILL`. It waits for the process and
D-Bus service to disappear, applies the adapter's `activity-exited` update,
and verifies that Left remains alive, owned, and activatable. It then shuts
Left down normally and verifies that both semantic hands are empty.

This closes the held-Activity crash-isolation gate. Shell/session resume while
a hand is held and unsupported object-capability refusal remain separate
requirements.
