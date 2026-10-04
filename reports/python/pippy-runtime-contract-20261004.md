# Pippy runtime contract

Date: 2026-10-04

Pippy now exposes the execution contract used by its native GTK4 Activity and
guest probe. Each run uses the current qualified Python interpreter in
isolated mode (`-I`), disables the user site, creates a disposable working
directory, and applies conservative child limits: 2 CPU seconds, 1 GiB
address space, 1 MiB file size, and 32 open files. Timeout and Stop terminate
the complete child process group.

The contract explicitly says `network not sandboxed`. This runner is bounded
local execution for an educational Activity, not a security sandbox. The
Activity shows this boundary next to the editor, and the guest probe validates
the same descriptor alongside output, error, timeout, and cancellation.
