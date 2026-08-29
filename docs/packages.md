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

The Activity Manager presents those same five numeric values as a centered
face scale: frowning face = Broken, unhappy face = Bad, neutral face = Needs
work, smiling face = Good, and the bright smiling face = Perfect. The face
selection is only another view of the existing numeric rating; it does not
reset or migrate the ratings file.

Each row is separated visually and includes the Activity summary, version,
remove action, and a contextual-help target. Activity metadata records the
bundle ID and any upstream help or repository URL declared by activity.info.
The maintained source inventory is documented in
docs/ACTIVITY-SOURCES.md.
