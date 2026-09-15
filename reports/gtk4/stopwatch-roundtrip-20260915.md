# GTK4 Stopwatch Journal resume evidence - 2026-09-15

Scope: prove that the native GTK4 Stopwatch Activity can resume a real Journal
object and render the restored elapsed time visibly, not merely launch as a
coverage surface.

Probe:

```sh
scripts/ssh-asp '/tmp/sugar-gtk4-stopwatch-roundtrip.py 2'
```

The probe runs inside the live Aspartame guest. It launches Stopwatch through
the GTK4 Journal service, stops it through Shell, finds the saved datastore
object, seeds that object's backing file with a JSON elapsed-time payload,
resumes the same object through Journal, verifies the visible elapsed-time text
through AT-SPI, and stops again.

Result:

```text
cycle=1 pid=513423 resumed_pid=513445 object=137fb924-aa66-4db6-9fb2-e779b9ad8d22 elapsed=124 resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=513465 resumed_pid=513485 object=c499d58b-1fc9-450c-a460-c261d9d436f4 elapsed=125 resume=PASS service-release=PASS shell-cleanup=PASS
stopwatch-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

AT-SPI emitted transient cache warnings while traversing the tree:

```text
AT-SPI: Error in GetItems ... /org/a11y/atspi/cache
```

Those warnings did not prevent process launch, visible elapsed-time discovery,
resume verification, service release, or shell cleanup. This evidence uses
AT-SPI and a seeded datastore payload; it does not prove physical keyboard
input, lap/export behavior, or collaboration parity.

Classification change: Stopwatch moves from COVERAGE IMPLEMENTATION to
FUNCTIONAL PORT for bounded elapsed-time Journal resume.
