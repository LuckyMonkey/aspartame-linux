# Installer plan

Do not build an installer in the bootstrap pass. Evaluate Calamares after the
live session is stable. The eventual flow must cover UEFI/GPT, automatic
partitioning, erase/install, optional encryption, user creation, locale,
keyboard, timezone, bootloader, and recovery. Installer-specific choices
should consume the same package/profile definitions as the live image.

