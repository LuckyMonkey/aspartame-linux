# Standalone image GTK3 key-handler verification — 2026-09-20

## Artifact

- ISO: `aspartame-2026.09.20-x86_64.iso`
- SHA-256: `b547ae6eac993fe758f3b37a2cfb52131307caa3dd7ee0d7c4258fa2d7e3b68f`
- Boot: clean QEMU boot without `/mnt/aspartame-dev`
- SSH diagnostic port: `2266`

## Root cause fixed

The image customizer applied the generated GTK3 navigation wrapper and then
overwrote `jarabe/view/keyhandler.py` with the GTK4 source copy.  The GTK4
module expects a `window-added` signal which the GTK3 `ShellModel` does not
provide, producing this startup traceback:

```text
TypeError: <shell.ShellModel ...>: unknown signal name: window-added
```

The image now preserves the pinned distro GTK3 handler at
`/usr/lib/aspartame/gtk3-keyhandler-upstream.py` before applying the wrapper.
The wrapper delegates to that copy in a standalone image; no GTK4 shell source
is installed into the GTK3 package.

## Runtime evidence

The rebuilt image booted both shell processes:

```text
753 python3 -m jarabe.main
1198 /usr/lib/aspartame/gtk4-preview/venv/bin/python .../sugar/src/jarabe/main.py
```

The classic process imported:

```text
wrapper  /usr/lib/python3.14/site-packages/jarabe/view/keyhandler.py
packaged /usr/lib/aspartame/gtk3-keyhandler-upstream.py
has window-added False
```

The classic Sugar session log contains normal D-Bus/service startup and no
`unknown signal name: window-added` traceback.  `/mnt/aspartame-dev` was not
mounted during this check.

## Remaining frontier

This closes a GTK3-reference boot regression.  It does not by itself prove
physical F-key delivery or complete GTK4 behavioral parity; those remain
separate runtime checks.
