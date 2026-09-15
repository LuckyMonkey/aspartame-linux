# Words GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-words-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=514367 resumed_pid=514389 object=e122b65d-c7fc-470e-8b6b-15fb5f163ac1 resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=514409 resumed_pid=514429 object=55de598c-d9c2-4f6e-8123-953cdaaec40e resume=PASS service-release=PASS shell-cleanup=PASS
words-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores `Aurora` through Journal and verifies the visible lookup
result before canonical Shell stop. Nonfatal AT-SPI cache warnings occurred
during cache restart.
