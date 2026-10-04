# GTK4 Activity share/join qualification - 2026-10-04

Scope: separate local Activity publication from the second-guest join
contract, so owner success cannot be mistaken for collaboration parity.

The owner probe was run with a bounded hold window:

```sh
SSH_PORT=2230 ./scripts/ssh-asp env \
  ASPARTAME_SHARE_MODE=shared ASPARTAME_SHARE_HOLD_SECONDS=30 \
  /usr/lib/aspartame/gtk4-preview/venv/bin/python \
  /mnt/aspartame-dev/scripts/sugar-gtk4-share-roundtrip.py
```

Owner result:

```text
share-roundtrip=PASS pid=41313 activity_id=f8867d837d74417c93fbe0e541304166 mode=telepathy-share
```

The peer probe uses `presenceservice.get_instance().get_activity(...)` and
calls the real `sugar4.presence.Activity.join()` method:

```sh
SSH_PORT=2231 ./scripts/ssh-asp env ASPARTAME_PEER_TIMEOUT=30 \
  /usr/lib/aspartame/gtk4-preview/venv/bin/python \
  /mnt/aspartame-dev/scripts/sugar-gtk4-share-join-roundtrip.py
```

Current result: the peer timed out before discovering the public Calculate
Activity. The owner path therefore remains qualified as publication only;
peer discovery/join and user-facing shared Activity actions remain open. The
qualification harness and clean-shell restart procedure are now in place for
the next network/session pass.
