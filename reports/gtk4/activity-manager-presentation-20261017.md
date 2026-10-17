# GTK4 Activity Manager presentation pass — 2026-10-17

The GTK4 Activity Manager now renders a standard Activity icon for each row,
resolves bundle-relative icon metadata, and falls back to `activity-start`
when metadata or artwork is missing. Rows also show an ellipsized description
with a localized `No description available.` fallback while retaining an
expanding information column and the existing launch/removal action contract.

The GTK-free presentation seam is covered by:

```text
tests/test_gtk4_activity_manager_presentation.py: 3 passed
tests/test_gtk4_activity_manager_section.py: 4 passed
tests/test_gtk4_snakepit_activity_manager.py: 2 passed
full repository gate: 575 passed
```

The rebuilt ISO is bootable and packages the new overlay file:

```text
aspartame-2026.10.17-x86_64.iso
sha256 34d4cf77e0e88badb256de25a0de032ceb57ae47c31235186e7d8e00f67b3cf9
```

Remaining evidence boundary: boot the new ISO, navigate to Settings →
Activity Manager, and capture the guest visual result. The source/build gate
does not claim that human visual check.
