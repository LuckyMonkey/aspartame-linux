# Settings lifecycle repair — 2026-10-22

Baseline: October 17 standalone ISO, booted with `QEMU_HEADLESS=1`,
`QEMU_SNAPSHOT=1`, and `QEMU_DEV_SHARE_MOUNT=0`. Existing disks were used
with temporary writes only. The guest reports `IMAGE_VERSION=2026.10.17`.

The original packaged `ShowControlPanel()` returned a false result and
failed to retain its window. Patch 0058's hunk length omitted its final two
lines. Corrected the hunk and added an idempotent repair for old exports to
both the preview build and ISO staging. The repair preserves upstream's
UTF-8 BOM and refuses unknown method endings.

After applying the repair to the temporary guest and restarting GTK4:

- Three Settings open → Home → reopen cycles passed.
- Duplicate modal Settings opens were refused during each cycle.
- About Computer tile discovery passed, but inventory visibility timed out
  after accessibility-generated tile clicking. Visual/refresh qualification
  remains open; no screenshot acceptance is claimed.
- Full host run: 581 passed, two ISO staging fixture failures because the
  fixtures lacked the newly required shell service source. Updated those
  fixtures to exercise the truncated-service repair and verify staged output.
- Focused regression rerun after fixture updates: 15 passed.

Next: rebuild the ISO with `make iso`, then run the guest probe with
`--lifecycle-only`. Continue About Computer tile/visual diagnosis separately.
No new ISO was built during this pass.
