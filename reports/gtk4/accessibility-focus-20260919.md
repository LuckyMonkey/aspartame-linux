# GTK4 accessibility focus — 2026-09-19

After selecting the modern Space and launching Help through the Journal
contract:

```text
help-visible=PASS help-search=PASS pid=34330 activity=2cec53a0490a4983966f67770268e5b8
focused=1 pid=27323 role=panel name='' path=panel < grouping < panel < Sugar < python
focused=1 pid=34330 role=text name='Search help' path=panel < panel < panel < panel < Sugar Help < -c
```

The AT-SPI probe temporarily pins the shared X11 `AT_SPI_BUS` property to the
modern Space's private registry and restores it afterward. The result shows a
real GTK4 Activity accessible tree and a focused Help search entry, alongside
the shell panel's focus representation.

The host QMP socket was unavailable for this particular post-rebuild Tab
injection attempt (`ConnectionRefusedError`), so this report does not claim a
new physical-key transport result. Existing physical keyboard evidence remains
separate from this AT-SPI focus evidence.
