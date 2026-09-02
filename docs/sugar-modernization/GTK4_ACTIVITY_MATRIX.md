# GTK4 activity matrix

No activity is marked usable until it launches inside a running GTK4 Sugar session.

| Activity | Pinned head | Import/build | Launch/toolbar/palette/Journal/clipboard/quit |
|---|---|---|---|
| Calculate | `1ff50e7` | not yet tested | not tested |
| Log | `b4c43c4` | not yet tested | not tested |
| Browse | `c448927` | not yet tested | not tested |
| ImageViewer | `87fedc0` | not yet tested | not tested |
| Terminal | `1425071` | not yet tested | not tested |


Home shell note (2026-09-02): Favorites/Home and the search List View render in
the pinned preview. The search path was exercised semantically and returned to
Home without a traceback. It correctly has no matches because these Activity
sources have not yet been built, installed, or registered as preview bundles.
