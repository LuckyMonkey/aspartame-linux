# 🧩 Activities:

> **Status:** stable GTK3 catalog + separately classified GTK4 coverage

The initial image uses Arch's signed Sugar GTK3 packages and a small set of
Fructose Activities. The current package group includes Browse, Calculate,
Chat, Clock, Imageviewer, Jukebox, Log, Paint, Pippy, Read, Record, Terminal,
Turtle Art, and Write.

Activity source uses `activity/activity.info`, `sugar-activity3`, and the
Sugar3 toolkit. Future Aspartame metadata may add isolated environment
declarations and inspect/clone actions, but those are not required for first
boot.

## GTK4 reading rule:

The modern inventory is intentionally reported in four classes:

- ✅ **FULL PORT** — normal workflow and semantics match the reference.
- 🛠️ **FUNCTIONAL PORT** — the principal workflow works with bounded scope.
- 🧪 **COVERAGE IMPLEMENTATION** — launch/render/lifecycle coverage only.
- 💤 **PLACEHOLDER** — shell-facing stub with no credible equivalent workflow.

See the [classification matrix](sugar-modernization/ACTIVITY_PORT_CLASSIFICATION.md)
before describing an Activity as “ported.” A successful launch is valuable
evidence, but it does not prove persistence, accessibility, collaboration, or
feature breadth.

![GTK4 Sugar Home](../reports/screenshots/sugar-20260915-151748-v0.0.31.png)

## Porting checklist:

1. Identify the GTK3 workflow and its Journal/object contract.
2. Give the GTK4 Activity a native surface and an accessible focus path.
3. Exercise pointer, keyboard, save/resume, stop, and abnormal exit.
4. Record the result and its boundary in the classification table.
