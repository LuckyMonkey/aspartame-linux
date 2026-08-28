# Boot and session startup

The live image enables NetworkManager, Bluetooth, CUPS, Avahi, and time sync.
tty1 autologins the `aspartame` user. Its `.bash_profile` runs `startx`, and
`.xinitrc` starts `sugar-session` inside `dbus-run-session`. This is a simple
prototype path; the eventual installed system should replace development
autologin with a deliberate account/session security model.

