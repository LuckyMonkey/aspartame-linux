# Packaged GTK4 qualification — 2026-10-04

## Image

- ISO: `aspartame-2026.10.04-x86_64.iso`
- SHA-256: `a48ecd3a142f62c9679a42bafa66409d81d3ffa88a0aae8a6d99dce92d2d160a`
- QEMU: headless VNC/QMP only, snapshot disks, 1920x1080 guest display
- Packaged Calculate and Finance entrypoint hashes match the checked-in sources.

## Results

- Guest visual sweep: `pass=2 fail=0` for Calculate and Finance.
- Calculate rendered centered at a readable width with a four-column keypad:
  [screenshot](headless-calculate-7-plus-8-packaged-20261004.png).
- Finance rendered Description and Amount side by side with aligned table
  headings: `visual-sweep-packaged-20261004-gtkfix/org.laptop.community.Finance.png`.
- QMP pointer macro entered `7+8` and produced `15`:
  [screenshot](headless-calculate-7-plus-8-packaged-20261004.png).
- AT-SPI Spaces action passed: `button=Spaces compare-action=PASS`.
- QMP framebuffer capture shows GTK3 and GTK4 side by side at 960x1080 each:
  [screenshot](spaces-button-packaged-20261004.png).

The semantic Spaces button/controller is qualified. Physical QMP F7/F8
transport remains open: the event reaches the guest, but the authoritative
workspace does not change in this environment.
