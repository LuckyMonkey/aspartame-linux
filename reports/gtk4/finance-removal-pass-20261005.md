# GTK4 Finance transaction-removal pass — 2026-10-05

Finance now has a complete bounded transaction lifecycle for the current
workspace:

- income and expense rows retain flexible descriptions and aligned amounts;
- every row exposes an object-specific accessible action (`Remove Grant`,
  `Remove Supplies`);
- removing a row rebuilds the visible table and recalculates the balance;
- the empty state returns when the last transaction is removed;
- the Journal payload preserves the remaining transaction list.

The [headless capture](finance-removal-20261005.png) was taken with:

```text
SSH_PORT=2230 ./scripts/ssh-asp \
  '/usr/lib/aspartame/gtk4-preview/venv/bin/python /mnt/aspartame-dev/scripts/sugar-gtk4-finance-roundtrip.py 1 /tmp/finance-remove-20261005.png'
```

Receipt:

```text
cycle=1 ... resume=PASS service-release=PASS shell-cleanup=PASS
finance-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

Finance now also exposes accessible CSV Import/Export actions. The pure CSV
boundary roundtrips income/expense direction and descriptions without changing
the JSON Journal payload. Chart views and collaboration remain outside the
bounded port; the CSV file-dialog path is implemented but still needs a visual
guest interaction receipt.
