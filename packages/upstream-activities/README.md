# Canonical Sugar Labs Activities

These are shallow source snapshots from official Sugar Labs repositories,
kept separately from Aspartame-authored Activities. They are copied into the
live development image by `scripts/install-canonical-activities.sh` and are
included in the repository for reproducible inspection.

Sources:

- TurtleBlocks: https://github.com/sugarlabs/turtleart-activity
- Memorize: https://github.com/sugarlabs/memorize-activity
- Maze: https://github.com/sugarlabs/maze-activity

Revisions are recorded in `REVISION-MANIFEST`.

Only bundles listed in `INSTALL-MANIFEST` are installed automatically. Other
official snapshots remain available for future porting work but are not
installed when their current runtime smoke test fails.
