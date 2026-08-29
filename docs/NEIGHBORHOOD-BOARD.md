# Neighborhood Board — future design

This document preserves a future Aspartame concept. It does not implement the
Board.

## Core idea

Every Aspartame person or machine in Neighborhood may expose a Bulletin Board.

> **IF IT ISN’T ON THE BOARD, IT ISN’T VISIBLE.**

The Board is an intentionally public surface, not filesystem sharing. A user
must deliberately place an object on their Board. Nothing else in their
filesystem or Journal becomes visible merely because the device is discovered.

Opening another machine in Neighborhood opens its Board, not its filesystem.

## Board objects

A user may deliberately place these kinds of objects on the Board:

- sticky or status notes;
- Journal objects;
- files and folders;
- photos;
- audio or video;
- URLs;
- Activity objects;
- collaboration invitations;
- discoverable services such as printers later, if their privacy model is
  explicit.

Objects retain semantic identity and should expose an appropriate action:

| Object | Primary action |
|---|---|
| Photo | View |
| Audio | Listen |
| URL | Browse |
| Document | Resume/Open |
| Note | Read |
| Activity | Resume/Join where supported |
| Printer | Print eventually |

The canonical interaction is:

```text
Journal object
    ↓ drag
My XO
    ↓
Put on Board
```

Removing an object from the Board removes ordinary Board visibility. It does not
necessarily delete the source object from the Journal or filesystem.

## Privacy and availability

Board publication is explicit and object-scoped. The Board must not become a
friendly-looking path to a user’s home directory, Journal database, or arbitrary
mounts.

Offline devices may retain cached Board metadata or status. The UI must clearly
show that the device is unavailable and must never imply that an unavailable
object can currently be retrieved. Cached metadata is not permission to expose
new content or to pretend a transfer succeeded.

## Transport direction

Discovery and transport should use boring, proven infrastructure where
possible. Investigate mDNS/DNS-SD plus an appropriate existing object-transfer
mechanism before inventing a protocol. Authentication, authorization, revocation,
and object lifetime need a design of their own.

SMB and SFTP may remain available as advanced conventional services, but they are
not the Board abstraction. A Board is a deliberate Sugar object surface with
semantic actions, not a disguised network share.

## Relationship to Sugar

Neighborhood answers “what is around me?” A discovered person or machine is a
place in that space. The Board answers “what did they deliberately leave out
for others?” This preserves Sugar’s spatial and social concepts while making
visibility explicit and safe enough for a general-purpose system.

Before implementation, map Board behavior to the existing Neighborhood,
palette, Activity, Journal, and collaboration lifecycles. Do not add a global
panel, filesystem browser, or conventional network share browser as a shortcut.
