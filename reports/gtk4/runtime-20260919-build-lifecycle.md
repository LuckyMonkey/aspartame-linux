# GTK4 rebuilt guest runtime — 2026-09-19

This report records evidence after the semantic patch-series cleanup and full
guest rebuild at commit `289e64d`.

## Build

Command, run in the guest development share:

```text
./scripts/sugar-gtk4-build.sh
```

Result:

```text
datastore metadata reader: PASS
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
Wayland socket will be owned by embedded Casilda at runtime
RESULT=0
```

## Space/runtime ownership

```text
./scripts/sugar-gtk4-runtime-check.sh gtk4
runtime-check=ok target=gtk4 pid=27323 desktop=1 window=0xe00005 stable_pid=758 gtk4_pid=27323
```

The modern process carried `ASPARTAME_GTK4_PREVIEW=1`, used the private preview
D-Bus session, and was selected on workspace 1 while the GTK3 reference stayed
on workspace 0.

## Repeated real Activity lifecycle

The probe launches through the shell Journal D-Bus contract, waits for the
Activity service and shell activation, calls `SetActive`, requests
`StopActivity`, and verifies the Activity process disappears.

Help (`org.laptop.HelpActivity`, three cycles):

```text
cycle=1 pid=28133 service-ready=PASS shell-active=PASS ... cleanup=PASS
cycle=2 pid=28235 service-ready=PASS shell-active=PASS ... cleanup=PASS
cycle=3 pid=28334 service-ready=PASS shell-active=PASS ... cleanup=PASS
lifecycle-probe=PASS
```

Count (`org.aspartame.Count`, three cycles after the rebuild):

```text
cycle=1 pid=28498 service-ready=PASS shell-active=PASS ... cleanup=PASS
cycle=2 pid=28605 service-ready=PASS shell-active=PASS ... cleanup=PASS
cycle=3 pid=28704 service-ready=PASS shell-active=PASS ... cleanup=PASS
lifecycle-probe=PASS
```

The PIDs differ on every cycle, demonstrating fresh process creation and
cleanup rather than reuse of a stale Activity.

## Scope

This is runtime evidence for startup, Casilda-backed Activity service
readiness, activation, stop, and cleanup. It does not by itself claim complete
behavioral parity for every Activity, peer collaboration, or abnormal-exit
coverage; those remain separate gates in the conversion tracker.
