# GTK4 Abacus UX pass — 2026-10-05

The visual sweep showed the former Abacus rod grid stretching its adjustment
buttons to the screen edges while compressing the bead display into a small
center strip. The GTK4 surface now provides:

- a centered, width-constrained place-value work card;
- a prominent current-value card with thousands grouping;
- readable place labels paired with each rod;
- direct clickable bead positions that set a rod value without requiring a
  separate adjustment control;
- stable 48px increase/decrease controls and a centered Clear action;
- preserved accessible labels and JSON Journal persistence.

The headless 1920x1080 capture was taken with:

```text
SSH_PORT=2230 ./scripts/ssh-asp \
  '/usr/lib/aspartame/gtk4-preview/venv/bin/python /mnt/aspartame-dev/scripts/sugar-gtk4-abacus-roundtrip.py 1 /tmp/abacus-ux-20261005.png'
```

It showed the seeded `Value: 12,345` state with the rods contained in the
centered card: [headless capture](abacus-ux-20261005.png). The same guest run
produced:

```text
cycle=1 ... resume=PASS service-release=PASS shell-cleanup=PASS
abacus-roundtrip=PASS direct-bead-action=PASS input-method=AT-SPI datastore-payload=seeded
```

This is UX and qualification progress, not a FULL PORT claim. Alternate bases,
custom abacus configuration, upstream feature breadth, and collaboration remain
open.
