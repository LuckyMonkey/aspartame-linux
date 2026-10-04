# Snakepit GTK4 Activity Manager bridge — 2026-10-04

## Result

The GTK4 Activity Manager now consumes user-owned Snakepit v0 JSON
qualification records from `ASPARTAME_SNAKEPIT_RECORD_DIR`.

- `PASS` records are shown as `Snakepit Python` only when their environment,
  working directory, command, and explicit launch contract are present.
- Qualified records offer `Launch` and run as a separate process with the
  recorded `PATH`, `VIRTUAL_ENV`, `PYTHONNOUSERSITE`, and `PYTHONPATH`.
- Failed or incomplete records remain visible as `Not ready` and are never
  presented as removable Activities.
- Native Sugar removal and approval behavior is unchanged.

## Verification

Focused checks:

```text
pytest -q tests/test_gtk4_activity_manager_section.py tests/test_gtk4_snakepit_activity_manager.py
6 passed

python3 -m py_compile gtk4-overlay/src/cpsection/activities/model.py gtk4-overlay/src/cpsection/activities/view.py
bash -n scripts/sugar-gtk4-run.sh
```

The synchronized GTK4 development guest rebuilt successfully:

```text
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
```

This qualifies the record-consumption and launch boundary, not arbitrary
package graphs, a security sandbox, or full Sugar Activity parity.
