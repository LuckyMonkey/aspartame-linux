# GTK4 Activity sharing control qualification

Date: 2026-10-04

## Result

The GTK4 Calculate Activity sharing control now completes the local action
round-trip in the headless development VM:

1. launch Calculate from the GTK4 Journal
2. open the Activity toolbar
3. activate the named `Share` control
4. activate the named `My Neighborhood` option
5. verify the `Sharing is unavailable` alert when no presence connection is
   active

Observed result:

```text
share-roundtrip=PASS pid=6071 activity_id=dacfa3a0a8b44025b0e0bdd87da41f0a fallback=visible-alert
```

The same probe passed after discarding the disposable VM state and rebuilding
from the patch series:

```text
applied GTK4 Activity sharing integration: 0180-toolkit-activity-sharing.patch
applied preview patch: 0181-toolkit-share-button-visible.patch
applied GTK4 radio palette accessibility: 0182-radiopalette-option-accessibility.patch
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
share-roundtrip=PASS pid=5168 activity_id=c1aed02d7d124738bbc84cbe8428f4d0 fallback=visible-alert
```

This is the private/no-presence qualification path. It proves the GTK4
control is visible to AT-SPI, actionable, and fails safely without claiming
that an Activity was shared. A real two-guest Telepathy join remains the next
qualification step.

## Fixes

- `0180`: connect GTK4 Activity share/join/invite behavior to the existing
  presence service.
- `0181`: give the Share toolbar control a neighborhood icon and accessible
  name.
- `0182`: give radio palette options their stored Sugar labels as accessible
  names.

No history, rewind, or unrelated RNG behavior was introduced.

## Reproduction

```bash
./scripts/sugar-gtk4-dev-sync.sh
SSH_PORT=2230 ./scripts/ssh-asp \
  'python3 /mnt/aspartame-dev/scripts/sugar-gtk4-share-roundtrip.py'
```
