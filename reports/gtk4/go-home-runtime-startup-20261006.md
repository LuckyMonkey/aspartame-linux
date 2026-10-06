# GTK4 Home action runtime qualification — 2026-10-06

The canonical `go_home()` action was rebuilt and exercised in a fresh,
headless QEMU snapshot. The initial implementation imported `frame` and
`shell` at module load time, which created a `BuddyMenu` circular import while
the shell started. Those imports now happen inside `go_home()`, leaving the
action available without pulling the frame/buddy modules into startup order.

Build receipt:

```text
verified existing semantic Spaces action menu: 0169-home-spaces-action-menu.patch
applied canonical go_home action: 0203-canonical-go-home-action.patch
sugar4: PASS
Casilda 1.0: PASS 1.0
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
```

Runtime receipt:

```text
Aspartame GTK4 Sugar preview
datastore: ready
WARNING:root:Running main
```

The development shell remained alive past initialization with no
`BuddyMenu` circular-import traceback. Color My World then passed its
headless collaboration-style roundtrip:

```text
cycle=1 ... resume=PASS service-release=PASS shell-cleanup=PASS
colormyworld-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The GTK4 retirement gate remains blocked on full-parity evidence and
collaboration-join qualification. This report does not claim either is
complete. No frame history, rewind behavior, or unrelated RNG coupling was
introduced.
