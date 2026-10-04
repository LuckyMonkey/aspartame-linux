# GTK4 Read UX pass — 2026-10-04

## Result

Read already rendered its sample document, but the page content floated in an
unbounded white workspace. The activity now presents the text inside a labeled
`Reading page` frame with a visible boundary, readable horizontal padding, and
the existing search and Previous/Next controls kept in the surrounding shell.

The UTF-8 Journal/form-feed page model is unchanged.

## Verification

Focused host check:

```text
pytest -q tests/test_gtk4_read_activity.py
2 passed
```

The rebuilt writable GTK4 guest preview passed:

```text
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
```

Read launched through the real Journal D-Bus path in the headless GTK4 shell.
The initial 1920x1080 capture showed the framed first page; its SHA-256 was
`f4988b87bf50c7f5806be6b13e8e4e817fc561b2e216928e57f0dba6c8774d33`.

A headless QEMU click on `Next` changed the page indicator to `Page 2 of 3`
and displayed the second page inside the same frame. The follow-up capture
checksum was
`8168fbd550ea96b7f559bc9f961732f6ead24fe29112dd2af43e6bbfaf07c7f3`.

## Boundary

Read remains a `FUNCTIONAL PORT`, not a `FULL PORT`. PDF/EPUB and full upstream
format breadth remain open. No GTK3 package was removed.
