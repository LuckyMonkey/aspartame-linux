# GTK4 Wayland preview runbook

This runbook runs only the isolated GTK4 preview. It never replaces the
working GTK3 Sugar installation.

## Required outer compositor

Jarabe's GTK4 migration uses Casilda for its inner `wayland-sugar` activity
compositor, but GTK itself still needs an outer display backend. The preferred
backend is a real Wayland session or a nested compositor such as Weston.

Check the current session:

```bash
printf 'DISPLAY=%s\nWAYLAND_DISPLAY=%s\nXDG_RUNTIME_DIR=%s\n' \
  "${DISPLAY-}" "${WAYLAND_DISPLAY-}" "${XDG_RUNTIME_DIR-}"
find "${XDG_RUNTIME_DIR:-/nonexistent}" -maxdepth 1 -type s -name 'wayland-*' -printf '%f\n'
```

The host must provide both `WAYLAND_DISPLAY` and the matching socket under
`XDG_RUNTIME_DIR`. Weston and Xwayland are host packages; install them through
the normal privileged package workflow, not inside the preview prefix.

## Run the preview

```bash
export GTK4_ROOT=/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4
GTK4_BACKEND=wayland make sugar-gtk4-check
GTK4_BACKEND=wayland make sugar-gtk4-build
GTK4_BACKEND=wayland make sugar-gtk4-run
```

The launcher reports the pinned shell/toolkit revisions, backend, socket,
private runtime, and log path. It fails before starting Python if the outer
socket is missing. The private runtime contains a symlink to the outer socket;
no host runtime files are changed.

For comparison only:

```bash
GTK4_BACKEND=x11 make sugar-gtk4-run
```

This uses the current display or private Xvfb and must not be described as a
Wayland test.

## Evidence required for a Wayland claim

Record:

- `GTK4_BACKEND=wayland` and `GDK_BACKEND=wayland` in the launcher output;
- the outer Wayland socket and compositor version;
- Casilda's inner `wayland-sugar` socket;
- Jarabe stdout/stderr and datastore log;
- a screenshot showing the Sugar shell;
- shell liveness and Home/Frame interaction checks.

A toolkit import, Casilda build, or X11 screenshot is not Wayland shell
verification.

## Current blocker

As of 2026-09-02 this development host is X11-only and has no installed
Weston/Cage. The Wayland-first launcher therefore fails cleanly with a
specific preflight message. This is an environment prerequisite, not evidence
of a source-level GTK4 failure.
