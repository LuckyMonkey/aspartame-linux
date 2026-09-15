# Moon GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-moon-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=515906 resumed_pid=515928 object=559c6887-cb3c-4653-9578-467869364d8c resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=515948 resumed_pid=515968 object=76ab5324-7f4a-48d7-8eb5-4bd6893f080f resume=PASS service-release=PASS shell-cleanup=PASS
moon-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores phase 4 through Journal, verifies the visible Full moon
readout, and performs canonical Shell stop on both cycles. Known nonfatal
AT-SPI cache warnings occurred during cache restart.
