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
   Activity replacement. **Qualified 2026-10-04** with a real Journal UID
   and a fresh GTK4 shell;
4. a fresh disposable image boots and qualifies without the GTK3 fallback;
5. the GTK3 fallback is not required by any remaining Activity, shell path, or
   recovery workflow.

Run the non-destructive gate check from the repository root:

```sh
bash scripts/sugar-gtk4-retirement-gate.sh
```

Current result remains deliberately `BLOCKED`: all registered Activities are
still classified FUNCTIONAL PORT rather than FULL PORT and peer Activity join
is not qualified. The shell/session restart requirement is now qualified; no
GTK3 package is removed by this check.

The first modern-space candidates remain Portfolio, Markdown, Finance, Write,
Pippy, Jukebox, Color My World, and Abacus. Their GTK4 surfaces and bounded
workflows are qualified, but candidate status is not package-removal approval.

## UX milestone — 2026-10-05

The first visual-sweep cleanup pass is in `Write`, `Portfolio`, and `Finance`:

- Write and Portfolio now present an intentional empty editor state inside the
  framed work surface, hide it as text is entered, and keep Save/Clear actions
  aligned at the footer edge.
- Finance keeps the description column flexible while constraining the amount
  column, and presents an intentional empty-ledger state instead of a blank
  table.

This is forward UX progress, not a retirement-gate claim. The next pass should
apply the same visual rule to the remaining sparse/table-heavy Activities and
then collect real workflow evidence for each candidate.

The follow-up pass also clarified Calculate history, Pippy output, and Jukebox
playback state. Calculate now labels and explains an empty history pane, Pippy
shows output as a deliberate run/result surface, and Jukebox keeps playback
status beside its actions while visually marking the selected track. Pippy's
bounded runner remains the forward path for the upcoming Python-runtime work;
it is not yet a claim of full upstream Pippy parity.
