# Headless Spaces button qualification — 2026-10-03

## Result

PASS for the supported semantic comparison path. The isolated QEMU instance
remained headless; no host QEMU window was mapped, activated, or given the
mouse.

- The guest-side AT-SPI probe activated `Spaces`, then
  `Compare Spaces side by side`.
- The source-mounted runtime reported:

  ```text
  spaces-menu=PASS button=Spaces compare-action=PASS
  Sugar Spaces side by side: GTK3=960x1080 GTK4=960x1080
  ```

- QMP `screendump` captured both panes in
  `spaces-button-headless-20261003.png`: GTK3 Color on the left and GTK4
  Home on the right.
- The GTK3 side remains a normal undecorated window in comparison mode, so
  Metacity no longer restores it as a maximized desktop window.

## Packaged ISO qualification

The same path was rerun from the rebuilt standalone image
`aspartame-2026.10.03-x86_64.iso` (SHA-256
`9e3c3bcb8272b121e91507fed70211a37c5717c744aed846d7580de47597bce3`).

- The packaged AT-SPI probe passed: `button=Spaces compare-action=PASS`.
- The QMP pointer/screendump macro passed without a host display; the
  resulting framebuffer is `spaces-button-packaged-20261003.png`.
- The packaged screenshot shows GTK3 and GTK4 side by side at 960x1080 each.
- QMP F8 transport still reports `before=0 after-f8=0`; it is delivered to the
  guest but does not switch the authoritative workspace in this environment.

## Reproduction

```sh
SSH_PORT=2223 \
  ./scripts/ssh-asp \
  'runuser -u aspartame -- env DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 \
   ASPARTAME_ATSPI_BUS=unix:path=/run/user/1000/aspartame-gtk4/at-spi/bus_0 \
   python3 /mnt/aspartame-dev/scripts/sugar-gtk4-spaces-menu-probe.py'

ASPARTAME_QEMU_QMP=/tmp/aspartame-qemu-qmp-headless2 \
  ./scripts/qemu-headless-macro.py macros/qemu/headless-one-click.json
```

Physical F7/F8 remains open separately: the F8 event reaches X11 in the
headless VM, but does not change `_NET_CURRENT_DESKTOP`. The semantic button
and controller are the reliable comparison path until that QEMU/Metacity
transport boundary is resolved.

No commit or GitHub push was performed.
