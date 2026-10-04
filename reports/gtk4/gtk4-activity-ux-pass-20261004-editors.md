# GTK4 activity UX pass — editor workspaces

Date: 2026-10-04  
Environment: headless QEMU, 1920×1080, GTK4 preview, no host mouse grab

Markdown and Pippy now present their primary work as explicit horizontal
workspaces rather than vertically stacked surfaces with weak or invisible
boundaries:

- **Markdown** has a labeled Markdown source pane beside a labeled live
  Preview pane, with the Clear action kept at the lower edge of the workspace.
- **Pippy** has a labeled Python program pane beside a labeled Output pane;
  Run and Reset example stay with the editor, and the status remains below the
  workspace.

Evidence:

- targeted visual sweep: `pass=2 fail=0`, 1920×1080;
- both bundles launched through the GTK4 Journal/D-Bus route, painted, were
  captured, and stopped cleanly;
- two Journal resume/stop cycles passed for each bundle, including seeded
  Markdown preview and Pippy source payloads;
- focused source tests: 4 passed;
- generated captures: [`visual-sweep-ux-editors-20261004/`](visual-sweep-ux-editors-20261004/).

This is a modern-space UX qualification, not a full GTK3 parity claim. The
GTK3 bundles remain installed as fallback/reference while behavior,
collaboration, and physical-input gates are completed.
