# GTK4 Home Activity accessibility — 2026-09-13

Home's custom `ActivityIcon` widgets now expose a GTK4 accessible label from
the bundle name, use the button role, and participate in keyboard focus. The
change is isolated to the GTK4 `favoritesview` path and preserves Sugar icon
rendering/activation. Patch `0073` is routed by the guest build script.

The live GTK4 shell restarted successfully with the change (PID 88456) and
its runtime invariant check remained valid. Full AT-SPI traversal is still a
separate verification item; this patch removes the previous absence of a
semantic identity on Home's primary interactive objects.
