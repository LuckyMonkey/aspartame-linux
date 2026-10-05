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

## Fresh headless rerun

A second bounded two-guest run on the rebuilt image repeated owner
publication (`share-roundtrip=PASS`) but the peer again failed in discovery,
before `Activity.join()` was reached. Both guests had the documented private
NIC (`10.77.0.1/24` and `10.77.0.2/24`) and Avahi was active; the peer's
`_presence._tcp` browse saw only its local records during this run. The owner
fixture was then terminated after its hold session stopped responding to SSH.

The join probe now emits `share-join=BLOCKED phase=discovery|activity-object|join`
and, with `ASPARTAME_PEER_DEBUG=1`, records contact handles, advertised
Activities, and candidate properties. This makes the current transport/session
failure measurable without conflating it with GTK4 UI behavior or looping the
same opaque timeout.

The live peer log also exposed a separate shell lifecycle race: duplicate
shared-Activity removal reached `ShellModel.remove_shared_activity()` after
Neighborhood cleanup and raised `KeyError`. Preview patch `0188` makes that
map removal idempotent. It is applied and dry-run verified against the live
guest source; a rebuilt two-guest join receipt remains outstanding.

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

## 2026-10-05 controlled headless rerun

The isolated-profile two-guest fixture now produces a stable, repeatable
three-phase result:

```text
owner: share-roundtrip=PASS mode=telepathy-share
peer:  public Calculate Activity discovered
peer:  share-join=BLOCKED phase=join
peer:  members=[] local_pending=[] remote_pending=[dbus.UInt32(1)]
```

The peer's `sugar4.presence.Activity.join()` command receives self handle 1,
but Salut keeps that handle in `RemotePendingMembers`. The owner sees the peer
as a known contact (current fixture handle 2) and the public room remains
without a member. This is the precise remaining collaboration blocker; the
GTK4 UI and owner publication path are no longer the ambiguous part of the
test.

The repository keeps the profile-isolation and join-state diagnostics. An
experimental remote-pending acceptance patch was not retained because the
live two-guest run did not qualify a join and must not be mistaken for a
solution.
