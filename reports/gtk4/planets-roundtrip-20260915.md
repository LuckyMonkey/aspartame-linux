# Planets GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-planets-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=515254 resumed_pid=515276 object=2b7caf79-18ad-4992-a8b5-f7783d1810cc resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=515296 resumed_pid=515316 object=382ba423-d30f-4ddc-9c01-35765473ccfe resume=PASS service-release=PASS shell-cleanup=PASS
planets-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores selected `Mars` state through Journal, verifies the visible
selection, and performs canonical Shell stop on both cycles. Known nonfatal
AT-SPI cache warnings occurred during cache restart.
