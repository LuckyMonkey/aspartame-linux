# GTK4 Chirality Activity replacement/resume - 2026-10-04

Scope: verify that a persisted semantic hand can attach a newly launched GTK4
Activity without losing its Journal object reference.

Probe:

```sh
SSH_PORT=2230 ./scripts/ssh-asp \
  /usr/lib/aspartame/gtk4-preview/venv/bin/python \
  /mnt/aspartame-dev/scripts/sugar-gtk4-chirality-resume-roundtrip.py
```

Result:

```text
chirality-resume-roundtrip=PASS object=dd27f8ef-f766-416e-8d0c-72fdacbae00a active=left replacement=891efcfd5e6f417184161ac1b1373145 payload=utf8 state-clean=PASS mode=single-surface
```

The probe creates and saves one UTF-8 Journal object, assigns its resumed
Write Activity to Left, then stops that client while deliberately retaining
the persisted hand record. A newly launched Write client opens the same UID;
the adapter's `resume` command replaces only the Activity ID, retains the
object reference, activates the new client, and verifies the restored text.
The final payload and semantic state remain clean.

This qualifies Activity replacement/resume on one visible surface. It does
not claim recovery across a full shell or data-disk restart, and it does not
define unsupported object-format policy.
