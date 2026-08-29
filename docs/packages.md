# Initial package policy

The first profile uses signed Arch packages. Sugar 0.121, its GTK3 toolkit,
datastore, and a small set of core Activities are explicit profile inputs.
CUPS is intentional core infrastructure. Firefox is the initial browser;
pacman remains available to advanced users. A future Aspartame repository and
Flatpak policy will be designed after the live system works.

## Activity manager

Sugar Settings includes an `Activities` section. It inventories Activity
bundles from the standard system and user Activity directories, stores a
per-user five-level quality rating (`Broken`, `Bad`, `Needs work`, `Good`, or
`Perfect`) in `~/.config/aspartame/activity-ratings.json`, and provides a
recoverable Remove action.

User-local bundles are moved to `~/.local/share/aspartame/removed-activities`.
System bundles use the fixed `pkexec` helper
`/usr/local/libexec/aspartame-remove-activity` and are moved to
`/var/lib/aspartame/removed-activities`; they are never recursively deleted.
The Sugar shell/activity registry may need a shell or full session restart
before a removed system bundle disappears from Home.
