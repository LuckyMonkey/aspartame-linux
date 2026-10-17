# About Computer

Aspartame extends Sugar’s existing `aboutcomputer` control-panel section; it
does not create a separate settings application. The overlay lives at
`archiso/aspartame/airootfs/usr/share/aspartame/cpsection/aboutcomputer/` and is
copied into Sugar’s extension directory during ISO customization.

The panel reads local, truthful sources: `/etc/os-release`, `uname`/Python
runtime information, `/proc/meminfo`, `/proc/uptime`, root filesystem usage,
and `lspci` when available. The distribution is identified as **Aspartame Linux
(Arch Linux)** when the image carries `IMAGE_ID=aspartame`; it no longer uses
`lsb_release`, whose legacy fallback reported Debian in the VM.

The expanded System section currently shows image version, kernel,
architecture, CPU, core count, memory, storage, graphics, display backend,
Python, hostname, and uptime. Missing optional values are shown as “Not
available” rather than preventing the panel from opening.

## GTK4 preview

The standalone GTK4 preview carries a native replacement at
`gtk4-overlay/src/cpsection/aboutcomputer/`. Its read-only inventory provider
uses the same local sources without importing the GTK3 extension: OS release,
`/proc`, DMI, `lspci`, environment, and Python/platform metadata. The panel
includes a `Refresh inventory` action and preserves the license and identity
sections. The registration patch is applied during the guest preview build and
also at ISO staging when the exported preview archive predates the patch.

Host coverage verifies normal values, missing-source fallbacks, registration,
and standalone staging. A fresh guest visual capture remains a separate
acceptance step.
