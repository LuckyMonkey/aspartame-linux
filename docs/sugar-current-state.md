# Current Sugar state — bootstrap research

Research date: 2026-08-28.

## Upstream revisions inspected

| Component | Repository | Current default-branch revision |
|---|---|---|
| Shell | `sugarlabs/sugar` | `c34bc0ddb33bc6de7350ac95e6bf8c8278e75788` |
| GTK3 toolkit | `sugarlabs/sugar-toolkit-gtk3` | `aff963edfaa839ad654f132c5be56507153bcedb` |
| Artwork | `sugarlabs/sugar-artwork` | `3c4854d3eec0ba9b02a9ad139462fd559e6c027d` |
| Datastore | `sugarlabs/sugar-datastore` | `7aa97e791432d26007a9f16d4214b2085380edec` |
| Runner | `sugarlabs/sugar-runner` | `c7e76297362b80e68846d824198ee65e980b44d0` |
| Terminal Activity | `sugarlabs/terminal-activity` | `e810f0397b6d105642d8653af41e7dc909b3302e` |

The shell is Python and the toolkit is GTK3-based. The datastore is the
Carquinyol service, with data and metadata under the user's Sugar profile.
Terminal uses `sugar-activity3`, Sugar3, and the datastore.

## Arch availability

Arch Extra currently provides the Sugar shell/toolkit/datastore and the
`sugar-fructose` Activity set. This is enough to justify testing official
packages before creating Aspartame forks. AUR is not foundational.

## Display/session reality

The current Sugar runner contains X11/RandR code and explicitly documents that
it works with Xorg, not Wayland. The bootstrap therefore starts Sugar under
Xorg. Upstream has a GTK4/Wayland transition effort, but that is future work.

Current source also shows limited multi-output handling. HiDPI, wallpaper,
notifications, and modern display behavior remain runtime-test items.

## Interaction architecture

Sugar remains activity-centric: Home launches Activities, Activities save
through the datastore/Journal, and the toolkit provides Sugar navigation and
Journal metadata. Conventional applications can be launched from Activities
or a terminal; the bootstrap adds no new application registry.

Neighborhood and Group are legacy collaboration concepts. Aspartame should
preserve their conceptual value while designing Neighborhood 2.0 as passive
service discovery and VPN as a deliberate trusted remote-network view.

## Compatibility risk

The main unknown is runtime compatibility with current Arch Python/GTK and
individual Activities, not package existence. The first practical test is an
official-package image and a recorded first failure. Only then should
Aspartame add PKGBUILDs or patches.

## Not yet tested

No ISO has been built or booted. Home, Journal, Browse, audio, CUPS runtime,
network access, HiDPI, multi-monitor behavior, and Activity stability remain
unverified.

