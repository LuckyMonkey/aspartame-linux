# Get Books GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-get-books-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=515484 resumed_pid=515507 object=6440f76b-e3e3-4f5d-90a3-474a7d5d0c66 resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=515528 resumed_pid=515549 object=310e5aa3-02de-4d1e-bf41-de0aeec79928 resume=PASS service-release=PASS shell-cleanup=PASS
get-books-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores the `The Secret Garden` selection through Journal, verifies
the visible title, and performs canonical Shell stop on both cycles. Known
nonfatal AT-SPI cache warnings occurred during cache restart.
