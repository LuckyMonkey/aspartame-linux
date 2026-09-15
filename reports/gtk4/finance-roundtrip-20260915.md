# Finance GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-finance-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=514266 resumed_pid=514288 object=a9fe14ab-1ebe-43ae-99bd-acfbc0544b43 resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=514310 resumed_pid=514330 object=f8c275c7-4ea5-4ed5-8c39-0d9910b1b6ea resume=PASS service-release=PASS shell-cleanup=PASS
finance-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores seeded income/expense JSON and verifies the computed
`Balance: 100.00` readout before canonical Shell stop. Nonfatal AT-SPI cache
warnings were observed during cache restart.
