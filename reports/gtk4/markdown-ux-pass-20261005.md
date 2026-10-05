# GTK4 Markdown UX pass — 2026-10-05

The Markdown Activity is intended to be a direct source/preview workspace. The
new surface makes that relationship legible at 1920x1080:

- equal, framed source and preview panes with stable minimum widths;
- a readable monospace Markdown source editor;
- a guided empty-source overlay after Clear;
- top-aligned preview content instead of vertically centered text;
- a concise character-count status and accessible Clear action.

The fresh headless capture is [markdown-ux-20261005-final.png](markdown-ux-20261005-final.png).
It was taken with:

```text
SSH_PORT=2230 ./scripts/ssh-asp \
  '/usr/lib/aspartame/gtk4-preview/venv/bin/python /mnt/aspartame-dev/scripts/sugar-gtk4-markdown-roundtrip.py 1 /tmp/markdown-ux-20261005-final.png'
```

The same run produced:

```text
cycle=1 ... resume=PASS service-release=PASS shell-cleanup=PASS
markdown-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

This is UX and runtime qualification progress, not a FULL PORT claim. Full
Markdown parser/rendering breadth and collaboration remain open.
