# Calculate GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-calculate-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=513969 resumed_pid=513991 object=3074522c-2630-4cff-b8d8-5a7ec7a50c44 resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=514011 resumed_pid=514031 object=ee710c77-3878-4d85-9680-57ff4ce14b93 resume=PASS service-release=PASS shell-cleanup=PASS
calculate-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe seeds the Journal backing file with `7 * 6`, resumes it through the
GTK4 Journal launcher, verifies both the restored expression and computed
result (`42`), then stops through the Shell service. The guest emitted the
known nonfatal AT-SPI cache warnings while restarting cache objects.
