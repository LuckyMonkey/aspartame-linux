# Get Books GTK4 runtime evidence — 2026-09-15

The real guest round-trip probe completed two launch/resume/stop cycles:

```text
cycle=1 ... resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 ... resume=PASS service-release=PASS shell-cleanup=PASS
get-books-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

This supports the existing FUNCTIONAL PORT matrix entry for the bounded
offline catalog/search/selection workflow. Network catalog and download parity
remain explicitly outside the claim.
