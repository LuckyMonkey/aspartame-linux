# Known issues

* The current development host is Ubuntu and does not have `mkarchiso`; ISO
  creation must run inside an Arch build environment.
* Sugar's current shell/session path is X11-oriented. Wayland support is an
  upstream/future investigation, not a bootstrap assumption.
* Sugar, toolkit, and the listed Activities now boot in the QEMU image; GUI
  activity-by-activity testing remains incomplete.
* Conda, Navigator, Jupyter, Print Activity, VPN, full Neighborhood 2.0, wallpaper,
  and modern Settings are architectural work only.
* The live image currently uses development autologin. An installed system
  must adopt an explicit security model.

