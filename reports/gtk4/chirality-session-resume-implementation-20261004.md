# Chirality session-resume implementation — 2026-10-04

## Change

Held GTK4 hands now retain the information needed to survive a modern-space
restart:

- the state file defaults to persistent user state rather than the runtime
  directory;
- each hand can retain its GTK4 bundle ID and Journal object UID alongside its
  current process-local Activity ID;
- `sugar-gtk4-session.sh` starts a bounded rehydrator after the new shell and
  Journal are available;
- `sugar-gtk4-chirality-session-resume.py` relaunches each declared bundle with
  its object UID, replaces stale Activity IDs, persists the new IDs, and
  reactivates the previously active hand;
- a hand without a bundle ID is reported as skipped rather than guessed or
  launched under a different Activity identity.

The state remains only the current Left/Right hands and active hand. No
history, rewind, previous-frame list, or launch event log was added.

## Host verification

```text
python3 -m py_compile scripts/aspartame_chirality.py scripts/sugar-chirality.py scripts/sugar-chirality-activity.py scripts/sugar-gtk4-chirality-session-resume.py tests/test_chirality.py tests/test_chirality_activity_adapter.py
bash -n scripts/sugar-gtk4-run.sh scripts/sugar-gtk4-session.sh
pytest -q tests/test_chirality.py tests/test_chirality_activity_adapter.py tests/test_chirality_space_bridge.py tests/test_gtk4_spaces.py tests/test_gtk4_home_preview.py tests/test_gtk4_runner_singleton.py
..............................................................           [100%]
62 passed in 0.48s
```

This is source/integration evidence. The full two-shell guest restart receipt
is still required before the GTK4 retirement gate can clear
`shell-session-restart`.
