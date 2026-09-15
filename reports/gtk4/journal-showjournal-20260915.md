# GTK4 ShowJournal verification — 2026-09-15

The guest build completed successfully after retiring semantically obsolete
0127 and recognizing the already-applied 0129–0132 Journal fixes. Casilda,
sugar-ext, datastore metadata, and the GTK4 preview build all passed.

Modern Space runtime verification:

```text
org.laptop.Shell.ShowJournal -> boolean true
display -> 1920x1080
```

The captured modern-Space surface remains a blank white canvas:
`reports/screenshots/sugar-20260915-090825-v0.0.31.png`. The healthy Home
capture immediately before the action was the classic Space; after explicitly
selecting the modern Space, the blank Journal surface is reproducible. This
keeps shell-embedded Journal presentation open rather than silently promoting
it from a service-return check.
