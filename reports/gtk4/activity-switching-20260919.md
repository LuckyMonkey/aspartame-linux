# GTK4 Activity switching evidence — 2026-09-19

Command:

```sh
python3 /mnt/aspartame-dev/scripts/sugar-gtk4-switching-probe.py
```

Live result:

```text
switching-probe=PASS activities=2 home-frame-home=PASS
```

The probe launched Count and Calculate as separate Casilda Activities, waited
for each Activity service and accessible surface, activated both, called the
semantic `ShowHome → ShowFrame → ShowHome` path, returned to each Activity, and
stopped both processes with cleanup checks. It pins the modern AT-SPI bus while
both Spaces are alive, so the result is not a GTK3 registry observation.

This closes the representative shell switching workflow. It does not claim
Casilda can raise an arbitrary previously mapped toplevel during Alt+Tab; that
public API boundary remains documented separately.
