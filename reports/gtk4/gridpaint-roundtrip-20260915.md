# Grid Paint GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-gridpaint-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=514919 resumed_pid=514941 object=33421604-ce58-4eb1-a401-e46cbf6c63bf resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=514961 resumed_pid=514981 object=678410d3-d269-447d-9cc3-2e50f7f492d5 resume=PASS service-release=PASS shell-cleanup=PASS
gridpaint-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores two selected cells through Journal, verifies the visible
selection summary, and performs canonical Shell stop on both cycles. Known
nonfatal AT-SPI cache warnings occurred during cache restart.
