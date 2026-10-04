# Shareless Journal persistence qualification — 2026-10-04

The current standalone ISO was booted headlessly with disposable copies of
both QEMU disks, `QEMU_SNAPSHOT=0`, and no `/mnt/aspartame-dev` share.

- ISO SHA-256: `0ba689624f6418e0cb0c5c5d1a3b064174640dbadc13a25fbe3e06c87b602363`
- Preview archive SHA-256: `5e196b1ef3908fb17054e279f3a6b4cdbf39c4958133977aa1bbf28a990f4978`
- Data disk after reboot: `/dev/vdb ext4 rw,relatime` mounted at `/home/aspartame`
- Development share: not mounted
- Marker checksum before/after reboot:
  `56a0372d5c3c70bf1000c4c2fba46b2fe193ed4504671c944cb91e5dcdd82fec`

The reusable `scripts/sugar-gtk4-journal-reboot-probe.py` performed:

1. `prepare`: launched Calculate through Journal, stopped it, seeded the
   Journal payload with `7 * 6`, and retained the object UID on `/home`.
2. A real systemd reboot of the disposable guest.
3. `verify`: resolved the same UID through the post-reboot datastore index,
   found the canonical post-reboot payload path, relaunched Calculate, and
   verified the live Activity surface and cleanup.

Probe results:

```text
journal-reboot-prepare=PASS uid=60f07591-31a3-4368-9da7-bd8880f3f132 payload=7*6
journal-reboot-verify=PASS uid=60f07591-31a3-4368-9da7-bd8880f3f132 payload=7*6 surface=PASS cleanup=PASS
runtime-check=ok target=gtk4 pid=1656 desktop=1 window=0x1000005 stable_pid=833 gtk4_pid=1656
```

The resumed 1920×1080 Calculate surface visibly contains `7 * 6` and `42`:
[`journal-reboot-calculate-20261004.png`](journal-reboot-calculate-20261004.png)
(SHA-256
`6e9b209a1f3c520fb5335d1c6cb3acf418313c70dfe553e05cd10d17ed79524d`).

The datastore rebuilt the physical object path from the persisted UID during
boot. The probe therefore deliberately resolves `store.get_filename(uid)`
after reboot instead of treating the pre-reboot path as stable.
