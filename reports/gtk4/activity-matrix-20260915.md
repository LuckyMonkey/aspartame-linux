# GTK4 Activity matrix frontier — 2026-09-15

After replacing the GTK3-only Terminal and WebActivity launch paths, the guest
matrix was rerun from a clean modern shell with `ACTIVITY_CYCLES=1`. All 49
registered bundles completed Journal launch, private Activity service readiness,
Shell activation, StopActivity, and process cleanup:

```
activity-matrix=PASS
```

The earlier Reversi cleanup failure was traced to an orphan left by an
interrupted matrix invocation; a fresh Reversi probe passed and the clean matrix
then passed through the final Read Activity. This is probe evidence for runtime
coverage, not a claim that every Activity has full behavioral parity.
