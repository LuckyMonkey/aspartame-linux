# GTK4 Activity sharing peer qualification

Date: 2026-10-04

## Result

The GTK4 Calculate Activity share path now publishes the owner's current
activity through Telepathy BuddyInfo.  A headless two-guest qualification
observed the public Activity from the peer guest:

```text
share-peer=PASS activity_id=e069f6eab6a640d388dbfe9cc51f6839 room_handle=1 name='Calculate Activity' private=False type='org.aspartame.Calculate'
```

The local AT-SPI share action also passed after the rebuild:

```text
share-roundtrip=PASS pid=23051 activity_id=b1200ab6c7ab4431b39253e72ed8e07a mode=telepathy-share
```

The local probe now verifies the live `GetCurrentActivity()` BuddyInfo tuple
as well as the Activity log, so it does not depend only on a log file being
flushed before cleanup.

## Fixes included

- `0183`: FriendsTray tolerates an Activity announcement while no app is active.
- `0184`: Neighborhood buddy/Activity removal is idempotent against duplicate
  Telepathy signals.
- `0185`: GTK4 sharing calls `SetCurrentActivity(activity_id, room_handle)`
  after the room is created, matching the classic Sugar Neighborhood contract.
- The guest build script now verifies the known semantic result of `0174` and
  routes/applies the new patches without weakening generic patch-drift checks.

## Qualification notes

Both guest builds completed with the full GTK4 toolkit, Casilda, sugar-ext,
Jarabe, and datastore result marked `PASS`.  The disposable two-guest Salut
setup can still lose its preferred connection after repeated shell/activity
churn; when that occurs the share control correctly reports that no active
presence connection is available.  Restarting the modern shell restores the
connection.  This is an environment repeatability issue to continue tracking,
not a GTK crash or a false successful share.

No frame history, rewind behavior, or unrelated RNG stream coupling was added.
