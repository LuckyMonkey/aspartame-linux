# Typing Turtle GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-typingturtle-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=515793 resumed_pid=515815 object=d54b031d-48e3-4417-b7e3-6b1bf56dfdf4 resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=515835 resumed_pid=515855 object=2e92de7d-e430-488c-a57a-e17f9bce3f1a resume=PASS service-release=PASS shell-cleanup=PASS
typingturtle-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores exercise index 2 through Journal, verifies the visible
`Type: journal` prompt, and performs canonical Shell stop on both cycles.
Known nonfatal AT-SPI cache warnings occurred during cache restart.
