# W12 — a refused shutdown no longer destroys the session — 2026-09-15

## Reproduction

From the modern Space: F6 to reveal the Frame, click the XO owner icon, choose
**Shutdown** from its palette. Aspartame's guest polkit refuses a
non-interactive `PowerOff`, which is the ordinary case on this image.

Before the fix the shell logged

    ERROR:root:Can not stop sugar via systemd
    dbus.exceptions.DBusException: org.freedesktop.DBus.Error.InteractiveAuthorizationRequired

and then exited, leaving a black screen with nothing shut down.

## Root cause

`SessionManager.shutdown_completed()` in `jarabe/model/session.py` attempted
the privileged call, caught `DBusException`, logged it, and fell through to

    # Always quit the shell model to ensure we exit
    self._shell_model.quit()

The comment states the defect: the shell was torn down whether or not the
system had agreed to do anything. A refusal was treated as permission to
destroy the desktop.

## Fix

`patches/gtk4-preview/0143-session-refused-shutdown-keeps-session.patch`

- `_request_system_shutdown()` performs the PowerOff/Reboot request and
  returns whether the system accepted it.
- `shutdown_completed()` quits only on success, or when the mode is logout,
  where quitting *is* the action. On refusal it clears the pending mode and
  returns, leaving the session running.
- `_report_shutdown_failure()` unbusies Home and raises a `NotifyAlert`
  through the existing alert surface.
- A refusal logs as a plain warning instead of `logging.exception()`, so a
  denied request no longer reads as a fatal traceback to a human or to
  `sugar-gtk4-runtime-check.sh`.

No new privilege broker, shutdown daemon or approval mechanism; the existing
buddy-menu confirmation and alert surfaces are reused.

## Evidence

The deliberate path already confirms before acting: choosing Shutdown raised
the existing alert *"An activity is not responding. You may lose unsaved work
if you continue."* with Continue and Cancel.

- **Cancel:** shell alive, `runtime-check=ok`, F6 reveals the Frame and
  Escape dismisses it.
- **Refused shutdown:** the shell survived the refusal and the log now reads
  a single clean line:

      WARNING:root:System refused the shutdown request:
      org.freedesktop.DBus.Error.InteractiveAuthorizationRequired: ...

  with Home still rendered (126047-byte capture) rather than a black screen.

Both Spaces healthy afterwards: `runtime-check=ok target=gtk4 pid=94652
desktop=1`, classic shell pid 90516 alive, F3 and F6 still working.

## Limitation, recorded rather than pursued

`initiate_shutdown()` stops every Activity and emits `shutdown_signal` to its
subscribers *before* the privileged call is attempted. So although the shell
no longer quits on refusal, a session whose shutdown was refused has already
had its Activities stopped, and in one observed run the session ended a short
time later through that teardown rather than through
`shutdown_completed()`.

Correcting that means asking for authorization before destroying any state -
a sequencing change in the session model, not a bounded interaction fix. It is
left open deliberately.

**What is fixed:** a refused privileged action is no longer itself the thing
that kills the shell, and it is reported honestly.
**What is not:** teardown still begins before authorization is known.
