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

## Follow-up trace

The hold-window propagation defect in the owner probe was fixed separately;
with the corrected probe, peer publication/discovery was observed:

```text
share-peer=PASS activity_id=631da2afe378437a9e85c9d648fa3caa room_handle=5 name='Calculate Activity' private=False type='org.aspartame.Calculate'
```

The real `sugar4.presence.Activity.join()` call still timed out.  D-Bus
inspection showed the peer text channel in `RemotePendingMembers` rather than
`Members`.  A focused owner-invitation experiment did not produce a stable
join and caused the system `telepathy-salut` daemon to abort on both guests.
The coredump stack terminates in `g_source_remove()` while destroying Salut's
`gibber_muc_connection` / multicast transport objects.  No GTK4 invitation
patch was retained because it did not fix the join and increased crash risk.

Qualification remains: owner publication and peer discovery PASS; peer room
join BLOCKED on the Salut transport/session failure.  This is now a concrete
daemon-level blocker, not an unobserved GTK4 Activity callback.
