# 📦 Installer plan:

> **Status:** planned packaging work; the QEMU image is the current reference

Do not build an installer in the bootstrap pass. Evaluate Calamares after the
live session is stable. The eventual flow must cover UEFI/GPT, automatic
partitioning, erase/install, optional encryption, user creation, locale,
keyboard, timezone, bootloader, and recovery. Installer-specific choices
should consume the same package/profile definitions as the live image.
## Boundaries:

- ✅ The live ISO boots into Sugar in the development VM.
- ✅ The ISO embeds the GTK4 runtime and Activities, and is qualified without
  the development share.
- 🛡️ Persistence and recovery must remain explicit during installation.

The installer must not silently turn a development share, test credential, or
preview checkout into a production claim. See [building](building.md) and the
[standalone image runbook](sugar-modernization/STANDALONE_IMAGE.md).
