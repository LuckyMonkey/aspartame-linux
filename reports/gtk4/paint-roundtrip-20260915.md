# Paint GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-paint-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=514809 resumed_pid=514831 object=a844425d-3cfc-460c-afd8-413f98c0060a resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=514851 resumed_pid=514871 object=10b58209-7cce-4997-92f9-5781d1f9a8a5 resume=PASS service-release=PASS shell-cleanup=PASS
paint-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores seeded stroke/color state through Journal, verifies the
visible `Red ink` status, and performs canonical Shell stop on both cycles.
Known nonfatal AT-SPI cache warnings occurred during cache restart.
