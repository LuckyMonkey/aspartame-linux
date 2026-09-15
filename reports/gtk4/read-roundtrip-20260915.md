# GTK4 Read Journal resume evidence - 2026-09-15

Scope: prove that the native GTK4 Read Activity can resume a real Journal
object and render the resumed text visibly, not merely launch as a coverage
surface.

Probe:

```sh
scripts/ssh-asp '/tmp/sugar-gtk4-read-roundtrip.py 2'
```

The probe runs inside the live Aspartame guest. It launches Read through the
GTK4 Journal service, stops it through Shell, finds the saved datastore object,
seeds that object's backing file with a two-page UTF-8 payload separated by a
form feed, resumes the same object through Journal, verifies the visible page
text through AT-SPI, and stops again.

Result:

```text
cycle=1 pid=513283 resumed_pid=513306 object=b135e847-e6cb-4592-881d-72900d61691d resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=513327 resumed_pid=513348 object=8771f30d-b2ac-4705-9dd4-4056d1dcb05b resume=PASS service-release=PASS shell-cleanup=PASS
read-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

AT-SPI emitted transient cache warnings while traversing the tree:

```text
AT-SPI: Error in GetItems ... /org/a11y/atspi/cache
```

Those warnings did not prevent process launch, visible text discovery, resume
verification, service release, or shell cleanup. This evidence uses AT-SPI and
a seeded datastore payload; it does not prove physical keyboard input or
PDF/EPUB format parity.

Classification change: Read moves from COVERAGE IMPLEMENTATION to FUNCTIONAL
PORT for bounded UTF-8 text-object reading. Full upstream Read parity remains
unclaimed.
