# GTK4 Activity lifecycle recheck — 2026-09-15

After restarting the QEMU guest with the current launcher and selecting the
modern Space, the real Help Activity completed two Journal launch/activate/
stop cycles:

```
cycle=1 pid=2218 service-ready=PASS shell-active=PASS ... cleanup=PASS
cycle=2 pid=2307 service-ready=PASS shell-active=PASS ... cleanup=PASS
lifecycle-probe=PASS
```

This confirms the keyboard transport investigation did not regress Casilda
surface ownership, Activity D-Bus readiness, or process cleanup.
