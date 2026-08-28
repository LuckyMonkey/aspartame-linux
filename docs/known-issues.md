# Known issues

* The current development host is Ubuntu and does not have `mkarchiso`; ISO
  creation must run inside an Arch build environment.
* Sugar's current shell/session path is X11-oriented. Wayland support is an
  upstream/future investigation, not a bootstrap assumption.
* Sugar, toolkit, and Activities have not yet been boot-tested in this image.
* Conda, Navigator, Jupyter, Print Activity, VPN, Neighborhood 2.0, wallpaper,
  and modern Settings are architectural work only.
* The live image currently uses development autologin. An installed system
  must adopt an explicit security model.

