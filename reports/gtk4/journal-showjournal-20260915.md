# GTK4 ShowJournal verification — 2026-09-15

The guest build completed successfully after retiring semantically obsolete
0127 and recognizing the already-applied 0129–0132 Journal fixes. Casilda,
sugar-ext, datastore metadata, and the GTK4 preview build all passed.

Modern Space runtime verification:

```text
org.laptop.Shell.ShowJournal -> boolean true
display -> 1920x1080
```

After correcting the stale unconditional `show_main_view()` return and
restarting the modern shell, the same action now renders the native Journal:
`reports/screenshots/sugar-20260915-091816-v0.0.31.png`. The capture shows the
Sugar top bar, Journal search, project controls, 415 Journal entries, row
actions, and the bottom frame. This is visual evidence in addition to the
boolean service result.

The repaired shell was then exercised with the three-cycle Write Journal
round-trip probe; all cycles reported `payload=PASS resume=PASS
service-release=PASS shell-cleanup=PASS`.
