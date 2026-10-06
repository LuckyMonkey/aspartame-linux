# GTK4 preview build reproducibility — 2026-10-05

The GTK4 preview build was rerun from the existing headless ISO guest after
the Home action milestone. The guest had an older partially-applied source
state, which exposed a real idempotence gap in the patch driver: the 0169
Spaces menu was already present, but its older textual context could not
reverse-apply, so the build reported patch drift.

The build driver now:

- recognizes an existing 0169 Spaces action menu by its semantic contract;
- applies 0169 with bounded compatibility fuzz when the menu is absent;
- keeps the same clean-source route for the later 0203 `go_home()` patch.

Guest receipt:

```text
verified existing semantic Spaces action menu: 0169-home-spaces-action-menu.patch
applied canonical go_home action: 0203-canonical-go-home-action.patch
sugar4: PASS
Casilda 1.0: PASS 1.0
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
```

Post-build checks also passed:

```text
GTK4 semantic action sources: py_compile PASS
pippy-runtime=PASS output=PASS error=PASS wall-timeout=PASS cancel=PASS isolated-runner=PASS runtime-contract=PASS
```

This qualifies the rebuild path and the bounded Python runtime probe. It does
not claim full GTK3 parity or close the collaboration-join retirement gate.
