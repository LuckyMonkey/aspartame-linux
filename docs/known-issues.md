# Known issues

- The current shell reload boundary recreates Sugar's private session D-Bus and
  Metacity while keeping Xorg alive. Survival of an independently running,
  unsaved Activity across that bus replacement has not been validated.
- The QEMU 9p development tree uses `security_model=none` and becomes
  root-owned on the host when initialized by the guest. `make sugar-reload`
  therefore needs one scoped host `sudo` authentication.
- The current shell log emits nonfatal PyGObject `g_value_type_compatible` and
  `buddy` property warnings. They remain visible in `make sugar-logs`; the root
  cause has not yet been isolated.
- The live image lacks synchronized pacman repository databases, so read-only
  `pacman -Q/-Qo` diagnostics emit warnings about missing `core`/`extra`
  databases. Installed package ownership queries still return the inspected
  local package database results.
- Artwork is still the upstream `sugar-artwork` package. This pass established
  how it works but did not add a hot-reloadable Aspartame artwork source tree.
- Sugar uses X11/Metacity and GTK 3. GTK4/Wayland migration was not attempted.
- A full graphical-session restart intentionally ends running Activities.
