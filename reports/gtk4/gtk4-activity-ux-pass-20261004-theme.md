# GTK4 shared theme UX qualification

Date: 2026-10-04

## Result

The shared Sugar GTK4 stylesheet now gives `title-1` Activity headings a
consistent 28px bold treatment and gives `heading` labels a clear secondary
hierarchy. A development-share synchronization gap was fixed at the same time:
`assets/gtk4` is now copied into the guest before the preview build, so visual
qualification cannot silently use an older theme file.

Representative Pippy evidence after a clean guest rebuild:

```text
visual-sweep=COMPLETE pass=1 fail=0 resolution=1920x1080
```

The rebuilt prefix contains the checked-in heading rules, and the Pippy
surface now presents a readable title above its side-by-side editor/output
workspace.

## Scope

This is a shared visual correction for all GTK4 Activities that use the Sugar
`title-1` or `heading` classes. It does not alter GTK3 theme files, Activity
data formats, or the GTK3 fallback/reference path.
