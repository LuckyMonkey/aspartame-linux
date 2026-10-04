# GTK4 retirement gate

GTK3 retirement is staged, not inferred from a launch matrix.

The forward path already hides supported GTK3 duplicates from the modern Home
registry while retaining the GTK3 bundles as fallback/reference. That is the
safe first stage: users exercise GTK4 without losing the known-good recovery
path.

The package-removal stage is intentionally blocked until all of these are
true:

1. every retirement candidate has a `FULL PORT` classification backed by GTK3
   comparison, real input, accessibility, persistence, and normal workflow
   evidence;
2. Neighborhood/Group Activity sharing and peer join pass as a real two-guest
   workflow;
3. held Chirality state survives a full shell/session restart, not only an
   Activity replacement;
4. a fresh disposable image boots and qualifies without the GTK3 fallback;
5. the GTK3 fallback is not required by any remaining Activity, shell path, or
   recovery workflow.

Run the non-destructive gate check from the repository root:

```sh
bash scripts/sugar-gtk4-retirement-gate.sh
```

Current result is deliberately `BLOCKED`: all registered Activities are still
classified FUNCTIONAL PORT rather than FULL PORT, peer Activity join is not
qualified, and full shell/session restart evidence is open. No GTK3 package is
removed by this check.

The first modern-space candidates remain Portfolio, Markdown, Finance, Write,
Pippy, Jukebox, Color My World, and Abacus. Their GTK4 surfaces and bounded
workflows are qualified, but candidate status is not package-removal approval.
