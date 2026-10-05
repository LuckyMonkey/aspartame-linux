# GTK4 Get Things Done parity pass — 2026-10-05

The GTK4 implementation previously supported adding and completing tasks, but
not the reference Activity's remove and reorder actions. The bounded task
contract now includes:

- add by Enter or the Add task button;
- completion toggling with an accessible CheckButton;
- remove with a named row action;
- move up/down actions that preserve the visible list order;
- JSON Journal persistence of task text, completion state, and order;
- an intentional empty-list state inside the Tasks frame.

The upstream Sugarizer Get Things Done reference uses the same task model
(title, completed state, remove, and reorder behavior); the comparison source
is [GetThingsDone.activity](https://github.com/llaske/sugarizer/tree/master/activities/GetThingsDone.activity).
This closes a bounded workflow gap; it is not being counted as a GTK3 FULL
PORT receipt. Collaboration, upstream packaging breadth, and live GTK3
visual/input comparison remain separate retirement gates.

Focused source coverage and Python compilation pass for this change. The
headless Aspartame guest receipt is:

```text
SSH_PORT=2222 ./scripts/ssh-asp \
  '/usr/lib/aspartame/gtk4-preview/venv/bin/python /mnt/aspartame-dev/scripts/sugar-gtk4-gtd-roundtrip.py 1'
cycle=1 ... resume=PASS service-release=PASS shell-cleanup=PASS
gtd-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

This confirms resume, Move Down, Remove task, order/completion persistence,
and clean Activity lifecycle in the guest. The classification remains
FUNCTIONAL PORT: collaboration, upstream packaging breadth, and live GTK3
visual/input comparison remain separate retirement gates.
