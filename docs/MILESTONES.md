# Milestones toward a good everyday OS

> **Status:** proposed sequence, written 2026-10-02. Each milestone ends in
> user-visible evidence, not a passing unit test alone. Dates are deliberately
> absent; order matters more than pace.

Aspartame already boots a standalone image into a real Sugar session, keeps
GTK3 as a working reference, and runs fifty GTK4 Activities with guest lifecycle
evidence in the modern Space (Record, the fifty-first, awaits its guest run). What it cannot yet do is live on someone's laptop: it does not
install, update safely, or cover everyday hardware. The milestones below close
that gap in the order that keeps each step testable.

The rule that runs through all of them is the project's existing one: **an item
is done when it has been shown working, and its limits are written down.**

## M0 — Finish the GTK4 conversion gate

The conversion is close enough that the remaining work is about evidence, not
new surfaces.

- [ ] Rebuild the preview and run the lifecycle matrix and
  `sugar-gtk4-record-roundtrip.py` in the guest; classify Record.
- [ ] Re-run the guest round-trips for the seven Activities the host harness
  fixed (Help, Jukebox, Count, Level, Finance, Mastermind, Stopwatch).
- [ ] Promote the first **FULL PORT**. Write, Calculate, and Terminal are the
  best candidates: each has a GTK3 reference in the image and a bounded core
  workflow. Record the F7/F8 side-by-side comparison as a checklist in
  `reports/gtk4/`, so later promotions copy one template.
- [ ] Bring up a second QEMU guest on a shared bridge so Neighborhood/Group can
  be exercised with a real peer. The "needs a second participant" gate is
  within the project's control; it should not stay open by default.
- [ ] Decide the `gtk4-verified` status vocabulary so `make
  activity-contract-check` runs again (see `known-issues.md`), and reconcile
  the five native rows in `REVIEWS.tsv` still marked `unreviewed`.
- [ ] Make the modern Space the default once the above hold, with the GTK3
  Space one keystroke away. Retiring GTK3 is a later, separate decision.

**Exit:** a person boots the image, lands in GTK4 Sugar, and every shipped
Activity either works or says honestly what it cannot do.

## M1 — Continuous evidence

Every later milestone depends on catching regressions before an ISO build.

- [x] Run the host suite, including the headless GTK4 Activity harness and real
  GStreamer captures, on every push (`.github/workflows/host-tests.yml`).
- [ ] Build the ISO in CI from a pinned Arch snapshot and publish its checksum.
- [ ] Boot that ISO headlessly in CI under QEMU and run the standalone
  acceptance sequence from `STANDALONE_IMAGE.md` (boot, both Spaces, one
  Activity launch/input/stop) with screenshots kept as artifacts.
- [ ] Track boot-to-Home time and idle memory per build; fail on large
  regressions once a baseline exists.

**Exit:** a broken shell, Activity, or image is visible on the commit that
broke it.

## M2 — Install to disk

- [ ] Choose between Calamares and a small Python installer Activity. Prefer the
  Activity if it can stay honest about partitioning; the first-boot experience
  should already feel like Sugar.
- [ ] UEFI/GPT, whole-disk install, optional LUKS encryption, bootloader, and a
  recovery entry, all built from the same package list as the live image.
- [ ] First-boot onboarding in Sugar's own terms: name, XO colours, language,
  keyboard, timezone, network.
- [ ] Journal and user data survive reboot on the installed system (the live
  image already proves this on a data disk).

**Exit:** install to a blank QEMU UEFI disk and to one real laptop; reboot into
Sugar; resume a Journal object created before the reboot.

## M3 — Safe updates and rollback

- [ ] Btrfs root with automatic pre-update snapshots and a boot-menu rollback
  entry.
- [ ] Update from a dated Arch snapshot plus the signed `[aspartame]` repository,
  so every machine on a given release sees the same package set.
- [ ] A Software Update section in Settings that runs pacman through a narrow,
  polkit-authorized D-Bus helper. Show what will change before it changes.
- [ ] Unattended security updates as an opt-in policy.

**Exit:** deliberately ship a broken update, observe the failure, and roll back
from the boot menu in one step without losing Journal data.

## M4 — Everyday hardware

Exercise each item on real machines, not only QEMU.

- [ ] Wi-Fi (WPA2/WPA3, enterprise, captive portals) from Sugar's Network view.
- [ ] Audio output and microphone selection through PipeWire; Record and
  Jukebox use the selected devices.
- [ ] Battery, brightness, and volume in the Frame; hardware keys work.
- [ ] Suspend/resume with running Activities intact.
- [ ] Cameras for Record; Bluetooth audio and input; printing via CUPS.
- [ ] HiDPI scaling, touchscreen input, and an on-screen keyboard.

**Exit:** a published hardware matrix for at least three real machines, each
row backed by a capture or log.

## M5 — Accessibility and language

- [ ] Orca speech across the shell and the GTK4 Activities (the AT-SPI names
  and roles already exist; this proves they are useful).
- [ ] High-contrast and large-text modes that survive a shell restart.
- [ ] Translations and input methods for at least one non-Latin script.

**Exit:** a keyboard-only and a screen-reader user can complete the standard
launch → work → save → resume loop without help.

## M6 — Software beyond Activities

- [ ] Flatpak as an application substrate behind the Activity launcher boundary,
  with the document portal mapped to Journal objects so saved work stays
  findable.
- [ ] Firefox and a small set of everyday applications presented as Activities.
- [ ] A Python environment Activity using conda/Miniforge, never the system
  Python.

**Exit:** install a conventional application, use it, and find its document in
the Journal afterwards.

## M7 — Wayland session and trust

- [ ] Run the modern Space as a full Wayland session, retiring X11/Metacity for
  it; Casilda remains the Activity surface boundary.
- [ ] Screen lock, multiple local users, and Secure Boot with signed images.
- [ ] Journal backup and restore to removable media.
- [ ] Harden the management plane (authentication, TLS, visible consent) before
  any classroom deployment.

**Exit:** a classroom-style pilot on real hardware for a full week, with issues
recorded in `docs/incidents/`.

## What this deliberately does not include

- A custom package manager, init system, or kernel.
- Converting Sugar into a conventional desktop to gain features quickly.
- Counting launch coverage as parity, or a QEMU-only result as hardware support.
