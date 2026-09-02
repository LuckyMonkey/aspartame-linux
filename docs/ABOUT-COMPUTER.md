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
