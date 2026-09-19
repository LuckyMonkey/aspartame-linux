# Standalone image runbook

This runbook defines the supported standalone build boundary for the current
GTK4 preview. The image is intended to boot without the development 9p share
(``/mnt/aspartame-dev``). That share remains useful for source iteration, but it
is not part of the image's runtime contract.

## What is packaged

The build consumes a pinned guest preview archive containing the GTK4 shell,
toolkit, Python environment, runtime data, and Activity prefix. The ISO staging
step installs it at:

```
/usr/lib/aspartame/gtk4-preview
```

The image also carries the current GTK4 overlay and the small Space/session
helpers under that root. `aspartame-x-session` starts the classic GTK3 Space as
the reference process and then starts the GTK4 Space from the packaged root.
When the development share is present it can still provide source overrides;
when it is absent the packaged tree is used directly.

## Build

The archive is generated from a completed pinned guest build and is kept out
of Git. It can be recreated from a guest-local checkout: the development
share is not required to build or run the exported image. Use an Aspartame
build guest with the profile's GTK4/wlroots/compiler dependencies installed.
The build guest and ISO package set must use a compatible Python version and
native-library ABI; this is a reproducible procedure, not a claim of
bit-for-bit reproducibility across rolling Arch package updates.

Inside the guest, as `aspartame`, start with a fresh checkout/build directory:

```bash
mkdir -p /home/aspartame/Projects
git clone https://github.com/LuckyMonkey/aspartame-linux.git \
  /home/aspartame/Projects/aspartame
cd /home/aspartame/Projects/aspartame
export GTK4_ROOT=/home/aspartame/Development/gtk4-preview
./scripts/sugar-gtk4-init.sh "$GTK4_ROOT"
./scripts/sugar-gtk4-build.sh
bash ./scripts/sugar-gtk4-export.sh /tmp/gtk4-preview-standalone.tar.gz
```

Use the same repository revision in the guest and on the ISO build host.
The initializer records upstream revisions in `PINS.tsv`; the build applies
this checkout's patches and compiles Casilda, sugar-ext, and the datastore
metadata reader. Run the exporter only after the build succeeds and while no
build is modifying its outputs. To export an already completed preview, run
only the last command with its `GTK4_ROOT` set.

The exporter includes `sources/`, `prefix/`, `venv/`, `PINS.tsv`, and just the
compiled schemas/group labels from `runtime/`. It excludes Journal/profile
data, settings, caches, compositor sockets, logs, and stale runtime Activity
copies. It preserves symlinks for the ISO staging step to resolve, always
uses `gtk4-preview/` as the archive root, and prints the resulting SHA-256.

On the host, copy the archive from the guest SSH port (the default QEMU
forward is `2222`; use your configured guest credentials):

```bash
mkdir -p /media/freezer/SteamLibrary/vms/aspartame-build/artifacts
scp -P 2222 aspartame@127.0.0.1:/tmp/gtk4-preview-standalone.tar.gz \
  /media/freezer/SteamLibrary/vms/aspartame-build/artifacts/
```

Then, from the matching host checkout with the Arch build root prepared, run:

```bash
SUDO_ASKPASS=/tmp/aspartame-askpass sudo -A \
  ./scripts/build-in-arch-root.sh
```

The script installs the ArchISO profile dependencies in the isolated build
root, rebuilds the one carried GTK3 toolkit package, stages the archive and
overlay into a temporary profile, and invokes `mkarchiso`. The resulting image
is written to `artifacts/out/aspartame-YYYY.MM.DD-x86_64.iso`.

For a different archive location:

```bash
GTK4_PREVIEW_ARCHIVE=/path/to/gtk4-preview-standalone.tar.gz \
  PROFILE=archiso/aspartame OUT_DIR=/path/to/out WORK_DIR=/path/to/work \
  ./scripts/build-iso.sh
```

The image embeds a `STANDALONE-MANIFEST` containing the archive SHA-256. This
makes it possible to identify exactly which preview was used without relying
on a host checkout.

## Boot and acceptance gate

Boot the produced ISO in QEMU or VirtualBox with at least 4 GiB RAM and a
1920x1080 display. A writable data disk is recommended for Journal persistence.
The acceptance sequence is intentionally user-visible:

1. Boot to the Sugar Home view with no `/mnt/aspartame-dev` mount.
2. Confirm the classic GTK3 Space starts and remains available as the reference.
3. Enter the modern GTK4 Space; confirm Home, Frame, Journal, Settings, and
   search render from the packaged tree.
4. Launch a representative native Activity (Calculate, Write, or Terminal),
   type real input, switch Home/Frame, then stop it. Confirm the icon and Frame
   state clear immediately.
5. Repeat launch/stop once more and inspect the Activity process list for no
   orphan. Seed and resume a Journal entry where persistence is under test.
6. Reboot the guest and repeat the Home → modern Space → Activity smoke path.

The development share is optional evidence, not a pass condition. A boot that
only works when `/mnt/aspartame-dev` is mounted is a development preview, not a
standalone image.

## Troubleshooting

* `/tmp/aspartame-gtk4-space.log` contains the modern Space startup trace.
* `STANDALONE-MANIFEST` identifies the packaged preview archive.
* `aspartame-sugar-info` reports the active shell/toolkit source origins.
* If GTK4 does not start, first verify
  `/usr/lib/aspartame/gtk4-preview/venv/bin/python` and the helper scripts exist;
  do not silently fall back to GTK3 and call the image healthy.

The stable GTK3 Space remains intentionally present while this gate is being
qualified. This is a packaging and reproducibility boundary, not a claim that
every Activity has identical GTK4 feature breadth.
