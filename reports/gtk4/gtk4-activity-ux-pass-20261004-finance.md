# GTK4 Finance UX qualification

Date: 2026-10-04

## Result

Finance now uses an expanding responsive workspace. The new transaction form
and its actions stay together, while the Transactions card keeps its
Description and Amount columns aligned without a fixed body or table minimum.
With no saved rows, the empty-state message is centered inside the card; when
rows exist, the list becomes the expanding content surface.

The focused headless development-guest visual sweep passed:

```text
visual-sweep=COMPLETE pass=1 fail=0 resolution=1920x1080
```

The updated screenshot is stored in the development share at
`reports/gtk4/finance-ux-20261004-v2/org.laptop.community.Finance.png`.

The seeded Journal resume and cleanup probe passed with two restored
transactions and the expected balance:

```text
cycle=1 ... resume=PASS service-release=PASS shell-cleanup=PASS
finance-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

## Changes

- Removed the desktop-sized body and table minimum so the workspace can shrink
  with the available Sugar surface.
- Kept a readable natural width for the amount field while allowing it to
  expand and contract with the form.
- Made the empty state a first-class centered state inside the Transactions
  card.
- Kept the existing JSON Journal payload and aligned transaction row columns.

This is development-guest evidence; the GTK3 Activity remains installed as a
fallback/reference until the broader retirement gates are met.
