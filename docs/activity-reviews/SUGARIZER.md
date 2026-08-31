# Sugarizer activity track

Sugarizer is a related Sugar-inspired web platform, not a replacement for the native Sugar Activity runtime.
Its repository stores activities under activities/ and describes them in activities.json.
Native Aspartame uses .activity bundles and activity.info, so the inventories stay separate.

References:
- Client: https://github.com/llaske/sugarizer
- Server: https://github.com/llaske/sugarizer-server

Planned review path:
1. Pin a Sugarizer client commit in an external review workspace.
2. Enumerate activities.json metadata.
3. Start Sugarizer in its supported desktop or web runtime.
4. Exercise one activity at a time and capture evidence.
5. Do not claim native Sugar compatibility without an explicit native bundle.

Initial overlap candidates include Calculate, Gears, Grid Paint, Maze, Memorize, Markdown, Turtle Blocks JS, and Clock.
