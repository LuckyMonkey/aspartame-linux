# Aspartame delivery milestones

This is the current five-milestone delivery track. Each milestone has an
acceptance boundary and an evidence trail; a passing unit test alone does not
claim guest or hardware parity.

Status: five milestones reached on 2026-10-17, with the remaining boundaries
called out below.

## M1 — Reproducible engineering baseline

**Status: complete.** Keep the generated Sugar patch copies synchronized with
the pinned Sugar archive and maintain a clean host gate.

Evidence:

- `make test`
- Sugar patch sync check
- 578 passing host tests

## M2 — Snakepit inspection and explanation

**Status: complete.** Provide read-only project inspection and explain an
existing qualification record without creating an environment or launching
software.

Commands:

```sh
python3 scripts/snakepit.py inspect ./project
python3 scripts/snakepit.py inspect ./project --json
python3 scripts/snakepit.py explain --record reports/python/example.json
```

The inspection reports declared requirements, direct conflicts, source
fingerprint, and candidate interpreter compatibility. The explanation reports
the verified level, selected environment, workflow result, and launchability.

## M3 — Evidence-backed isolated Python workflows

**Status: complete.** Qualification, launch, dependency-tension refusal, and
coexisting dependency versions must remain reproducible and must not modify
system Python.

Evidence:

- `make snakepit-qualify`
- `make snakepit-launch-check`
- `make snakepit-dependency-tension`
- `make snakepit-dependency-pair`
- `tests/test_snakepit.py`

## M4 — GTK4 behavioral regression gate

**Status: complete for the host gate; guest visual parity remains a separate
qualification.** Keep GTK3 as the behavioral reference, maintain the activity
matrix, and require lifecycle/persistence tests before promoting changes.

Evidence:

- `make test`
- GTK4 activity matrix: 51 entries, 49 native
- QEMU/guest visual and physical-input checks remain explicitly separate

## M5 — Bootable ISO release artifact

**Status: complete for image production.** Build the pinned Arch image,
produce a bootable ISO, and record its checksum. QEMU boot and human visual
inspection are follow-up runtime evidence, not inferred from ISO creation.

Latest artifact:

```text
aspartame-2026.10.17-x86_64.iso
sha256 ebff439e18fb7709dadd6965c7bd74b1a2e5e059d8a81f990b43637fa8509302
```

Build command: `make iso`.
