# GTK4-023 — AT-SPI bus discovery collision on the shared X display — 2026-09-15

`scripts/sugar-gtk4-help-visible.py`, previously verified, now fails:

    activate 18a0709d7aab42f59eab08931d3bd34a 0
    AssertionError: Help surface not visible in AT-SPI

Root cause, isolated live in the running guest (GTK4 shell pid 15138, GTK3
shell pid 23078, both already running; GTK3 had been restarted more
recently, at 15:16:24, than GTK4's 11:08:23):

- Each Space runs its own private `at-spi-bus-launcher` /
  `at-spi2-registryd` triple on its own deterministic socket
  (`$GTK4_ROOT/runtime/at-spi/bus_0` for the modern Space,
  `/run/user/1000/at-spi/bus_0` for the classic Space).
- `at-spi-bus-launcher` advertises its bus by writing the shared X11 root
  window's `AT_SPI_BUS` property. That property is a single global value per
  X display; whichever launcher starts most recently overwrites it.
- `Atspi.get_desktop(0)` (current at-spi2-core) discovers the registry
  through that root-window property. It does **not** honor an `AT_SPI_BUS`
  environment-variable override — a direct test with the variable exported
  and confirmed present in `os.environ` still resolved to the classic Space's
  bus.
- Net effect: any AT-SPI probe run after GTK3 was (re)started walks GTK3's
  tree (`metacity`, `-m`, `datastore-service`) and silently never sees the
  modern shell at all, with no error until a specific assertion fails.

This is a testing-infrastructure defect, not a shell defect: GTK4's own
accessibility export is unaffected (it registered against its own bus at its
own startup and stays there); only *external* discovery via the shared root
property is broken by Space restart ordering. Anything checked off as
"AT-SPI names/roles" evidence should be treated as ordering-sensitive until
probes are fixed.

## Fix

`scripts/sugar-gtk4-focus-probe.py` now saves the root window's current
`AT_SPI_BUS` value, temporarily overwrites it with the modern Space's own
deterministic socket path, runs the AT-SPI query, and restores the original
value in a `finally` block — mirroring exactly what `at-spi-bus-launcher`
itself does, scoped to the probe's own runtime so neither Space's
already-established AT-SPI connections are disturbed. Verified:

    focused=1 pid=15138 role=panel name='' path=Sugar < python

`sugar-gtk4-help-visible.py` and any future AT-SPI probe should use the same
save/swap/restore pattern rather than assuming the shared property already
names the intended Space.

## Related, separately observed

Before this fix was applied, the live guest was also found with the classic
GTK3 shell's window placed on workspace 1 (the modern Space's desktop),
covering/focusing over the running GTK4 shell — `sugar-gtk4-space.sh setup`
was re-run to reconcile placement. `require_gtk3`/`start_gtk4` only place a
process on its workspace when the space controller itself launches or
selects it; a bare `python3 -m jarabe.main` restart outside the controller
(as happened here) inherits Metacity's default same-desktop placement
instead. This is a plausible root cause for any other current session
reporting "Space" desktop mismatches when a shell was restarted directly
rather than through `sugar-gtk4-space.sh`.
