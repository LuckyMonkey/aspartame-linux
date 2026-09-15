# Get Things Done GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-gtd-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=513786 resumed_pid=513808 object=02de5c09-649a-44cb-972b-f7123072d5e6 resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=513828 resumed_pid=513848 object=40847a06-5e70-40d4-9c27-d8510ca27dd5 resume=PASS service-release=PASS shell-cleanup=PASS
gtd-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe seeds the saved JSON Journal payload with two tasks, resumes the
same object, verifies the visible `2 tasks · 1 complete` summary, and then
stops through the Shell service. AT-SPI emitted cache `GetItems` warnings while
the guest bus restarted cache objects; the target text and all lifecycle
assertions still passed. This evidence supports the bounded FUNCTIONAL PORT
classification, not full upstream task collaboration parity.
