# Boot and session startup

> **Status:** current development boot path · **Evidence:** QEMU runbooks 🥾

The live image reaches `graphical.target`, enables the intended system
infrastructure, and starts tty1 autologin for the development `aspartame` user.
There is no display manager.

```text
getty@tty1 → login → ~/.bash_profile → startx → Xorg + ~/.xinitrc
           → /usr/local/bin/aspartame-x-session
           → dbus-run-session → aspartame-session → sugar → jarabe.main
           → Metacity, Home, Frame, Journal, notifications
```

`.xinitrc` is intentionally stable and delegates to a system-owned script so a
persistent home directory cannot silently retain stale session logic. Migration
backs the prior file up once. The system-owned session currently respawns the
Sugar D-Bus island after shell exit while leaving Xorg alive.

For exact units, process boundaries, environment, restart semantics, and
recovery, see [SUGAR-DEVELOPMENT.md](SUGAR-DEVELOPMENT.md).

## What a healthy boot looks like:

- 🖥️ tty1 reaches the graphical target and starts Xorg.
- 🔐 the development user logs in without a display manager.
- 🧬 one D-Bus session owns the selected Sugar Space.
- 🏠 Home appears before Activities are launched.
- 🧪 the runtime check reports the expected GTK process and display.

If Home is absent, capture the session log before restarting. The recovery
sequence is deliberately observable: identify the owner, preserve the log,
then restart the smallest failed boundary.

![Booted Sugar Home](../reports/screenshots/sugar-20260915-151748-v0.0.31.png)
