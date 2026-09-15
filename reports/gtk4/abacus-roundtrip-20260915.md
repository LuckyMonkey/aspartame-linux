# Abacus GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-abacus-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=515032 resumed_pid=515054 object=a349ce19-0f8e-49d6-b883-20dd2321d703 resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=515074 resumed_pid=515094 object=d70665c4-2b8c-48c9-82aa-3f7bcb182ce2 resume=PASS service-release=PASS shell-cleanup=PASS
abacus-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores seeded rod values through Journal, verifies `Value: 12345`,
and performs canonical Shell stop on both cycles. Known nonfatal AT-SPI cache
warnings occurred during cache restart.
