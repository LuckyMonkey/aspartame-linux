# Authoritative GTK4 registry selection

Starting HEAD: 7397b45. Owner: Jarabe preview registry.

## Closed gap

Clock launch selected /usr/share/sugar/activities/clock.activity with
sugar-activity3, although the modern Clock.activity was installed.
Patch 0096 guessed the modern path from the legacy basename, and returned
an unregistered object. This also prevented 0095 from reliably replacing
the legacy registry entry. Home iteration and lookup could disagree.

Patch 0124 removes lookup-time scanning. Registration now prefers an explicit
sugar-activity4 command in either scan order, regardless of directory name
or legacy version. Normal same-runtime version policy and the classic
environment remain unchanged. No new runtime abstraction was introduced.

## Evidence

- Full guest build passed beyond 0015 and applied 0124.
- Fresh GTK4 shell PID: 469335.
- Journal GetBundlePath returned runtime/activities/Clock.activity and
  runtime/activities/Help.activity.
- Clock PID 469559, ID 7ab017b786ae4cf787019dbb8396ba27, remained visible at
  1920x1080. See clock-registry-fixed-20260914.png.
- QEMU pointer click at (1886,34) requested Stop. The process was gone by the
  next matrix Clock launch (new PID 469722).
- ACTIVITY_CYCLES=1 sugar-gtk4-activity-matrix.sh: all 50 entries passed;
  first PID 469630, final Read PID 471113, activity-matrix=PASS.
  These probes prove process creation/termination; they do not wait for
  every surface to map and do not prove per-Activity behavioral parity.
- pytest -q: 225 passed, including seven behavioral registry tests applying
  the actual patch to the pre-fix registry method fixture.
- GTK3 Journal introspection succeeded when run as aspartame on its bus.
  The earlier claim that this bus was closed was incorrect: root authentication
  failed. GTK3 Activity launch/input/stop still needs separate verification.

## Remaining frontier

Several modern metadata files name missing SVG paths despite an existing SVG
with another name. Fix those references next. Existing matrix and status
claims must retain the process-coverage limitation above.

Reproduce:

    ./scripts/sugar-gtk4-dev-sync.sh
    scripts/ssh-asp 'cd /mnt/aspartame-dev && ./scripts/sugar-gtk4-build.sh'
    scripts/ssh-asp 'cd /mnt/aspartame-dev && ACTIVITY_CYCLES=1 ./scripts/sugar-gtk4-activity-matrix.sh'
    pytest -q tests/test_gtk4_registry_precedence.py

Guest build still prints pre-existing root/user Git ownership diagnostics and
Graphene version warnings. The successful build is not a zero-warning claim.
