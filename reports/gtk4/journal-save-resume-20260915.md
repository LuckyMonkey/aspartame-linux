# Journal document retention and resume — 2026-09-15

Starting HEAD: `9303c7e`. Current runtime testing contradicted the earlier
implication that successful launch/stop cycles proved safe document closure.

## Closed gaps

1. **Shell Stop lost document data.** Before patch 0125, Write PID 499652
   contained `Aspartame resume proof 20260915 — café`. Stop returned true,
   but Journal object `988a9c4f-f074-4782-ab4e-5e28f34f241c` had no file.
   The shell issued window-close and immediate SIGTERM, interrupting toolkit
   save processing. ShellModel now requests the existing Activity `Close`
   service asynchronously. The Activity retains its surface until saving
   completes, or may keep it open to report a save failure. Frame callers
   already use this same ShellModel `stop()` method.
2. **Resuming a stopped Activity lost the object identity.** After fixing
   Stop, datastore content was correct but the resumed Write window was empty.
   The factory set `SUGAR_OBJECT_ID`, while activityinstance constructed its
   handle from `--object-id`. Patch 0126 forwards object and URI arguments
   through the existing launcher contract.

## Evidence

`journal-roundtrip-20260915.log` records three complete real-process cycles:
edit via AT-SPI, shell Stop, process exit, service release, datastore payload
inspection, launch the same object in a new PID, verify restored text, Stop
again, verify retained payload and shell cleanup. Test objects remain in the
preview Journal for inspection. No mocks or forced termination are used.

| Cycle | Initial PID | Resumed PID | Journal object |
| --- | --- | --- | --- |
| 1 | 506471 | 506494 | f76ccaed-7058-4f82-856b-1350705ff963 |
| 2 | 506514 | 506534 | 720dda99-a25a-48bf-9bf1-1eb931b34d8f |
| 3 | 506554 | 506574 | aec3006c-9ea5-4bc0-86eb-c96f3c684850 |

`write-restored-20260915.png` was inspected: the live 1920×1080 Casilda surface
contains both restored lines, accented text, and `Draft restored (62 characters)`.
This is an AT-SPI interaction test, not physical keyboard evidence.
The AT-SPI client emits cache-path warnings when discovering new Activity
processes; those warnings are visible in the transcript, not suppressed.

## Reproduce

Host:

```sh
./scripts/sugar-gtk4-dev-sync.sh
scripts/ssh-asp 'cd /mnt/aspartame-dev && ./scripts/sugar-gtk4-build.sh'
```

After starting the rebuilt modern shell, with no Write process already open:

```sh
scripts/ssh-asp 'python3 /mnt/aspartame-dev/scripts/sugar-gtk4-journal-roundtrip.py 3 /tmp/write-restored.png'
```

Host regression suite: `pytest -q` — 271 passed. Full guest build passes
through 0126; previous ownership/version-reporting warnings remain present.
Runtime libraries: GTK 4.22.4, Casilda 1.5.0, wlroots 0.20.2, Python 3.14.

All 50 registered modern Activities passed one service-ready/activate/stop
cycle after the fix (`save-safe-activity-matrix-20260915.log`). This tests
the shared stop-path regression; it is not a 50-Activity parity claim.
Semantic Spaces switching and runtime checks passed for classic PID 496608
and modern PID 506262 (`journal-spaces-20260915.log`). No GTK3 code changed;
this round checks GTK3 shell availability, not its full Activity catalog.

### Save failure and cancellation

A separate live Write test used Activity ID
`f783113760524c14beca2dcd546c3b19`. Its own `instance` directory was temporarily
changed from mode 0755 to 0500, while its parent directories and the datastore
remained untouched. Stop triggered the expected PermissionError. The process
remained alive, AT-SPI still read `Save failure preserves this draft`, and the
native alert exposed `Don't stop` and `Stop anyway`. Permissions were restored
to 0755 in a `finally` block.

Activating `Don't stop` through AT-SPI kept the Activity open. Editing the text
to `Draft edited after cancelling Stop` and retrying shell Stop then wrote that
exact payload to Journal object `4d269299-26a5-4371-a8b1-a305bb0a76c9` and exited.
This verifies the save-failure/cancel/retry route; physical input and the
intentional-discard button are not covered by this particular test.

## Ownership and next gap

0125 belongs to Jarabe and retires the forced-stop behavior of 0063–0065.
0126 belongs to the toolkit launcher. Both are upstream candidates and use
existing APIs. No new runtime service, abstraction, or dependency was added;
the new script is test scaffolding only.

Write is now classified FUNCTIONAL PORT: its principal plain-text editing and
Journal workflow is evidenced, while rich-text and document-format parity are
outside this bounded port. The full GTK4 completion gate remains open. Next:
verify other real Activity workflows that depend on this restored Journal
boundary and rank remaining shell gaps from runtime.

Correction to the earlier Stopwatch diagnostic: its first failed probe used
the wrong bundle ID (`org.sugarlabs.Stopwatch`); that failure did not establish
a stale registry. The correct ID is `org.sugarlabs.StopwatchActivity`.
