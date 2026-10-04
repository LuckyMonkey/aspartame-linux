# Headless Spaces side-by-side qualification — 2026-10-04

## Result

PASS for the supported semantic comparison path. QEMU ran with no host display
(`QEMU_HEADLESS=1`, `QEMU_DISPLAY=none`, snapshot disks, and a private QMP
socket).

- The guest AT-SPI probe activated `Spaces`, then `Compare Spaces side by
  side` from the GTK4 Home button.
- Geometry qualification passed at 1920×1080:
  `GTK3=960x1080+0+0`, `GTK4=960x1080+960+0`, both on workspace 0.
- The delayed QMP framebuffer capture visibly renders both Homes side by side:
  [spaces-side-by-side-headless-20261004.png](spaces-side-by-side-headless-20261004.png)
- The qualification command completed with `spaces-qualification=PASS`.

The GTK4 runtime itself came from the ISO; the new geometry probe was
source-mounted through `/mnt/aspartame-dev`, matching the normal development
qualification workflow. `scripts/build-iso.sh` now stages that probe for the
next image build.

ISO: `aspartame-2026.10.04-x86_64.iso`  
SHA-256: `a00d5460a2c99862c682911eaa349a872f0e3be5cbc38bd138fca84463f0f9c7`

The probe now waits for the controller’s GTK3 restart and GTK4 window map
before checking geometry. The framebuffer macro waits five seconds after the
semantic action so startup does not produce a misleading black GTK4 pane.

Physical F7/F8 remains a separate open QEMU/Metacity input-transport check;
this qualification intentionally uses the reliable button action.
