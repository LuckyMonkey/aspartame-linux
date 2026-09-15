# 📦 Installer plan:

> **Status:** planned packaging work; the QEMU image is the current reference

Do not build an installer in the bootstrap pass. Evaluate Calamares after the
live session is stable. The eventual flow must cover UEFI/GPT, automatic
partitioning, erase/install, optional encryption, user creation, locale,
keyboard, timezone, bootloader, and recovery. Installer-specific choices
should consume the same package/profile definitions as the live image.
## Boundaries:

- ✅ The live ISO boots into Sugar in the development VM.
- 🧪 GTK4 source overlays are mounted during preview validation.
- 🚧 A handoff ISO must embed the selected sources and Activities before it is
  called self-contained.
- 🛡️ Persistence and recovery must remain explicit during installation.

The installer must not silently turn a development share, test credential, or
preview checkout into a production claim. See [building](building.md) and the
[GTK4 bootstrap runbook](sugar-modernization/GTK4_BOOTSTRAP.md).
