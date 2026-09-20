# Standalone image reboot and persistence evidence — 2026-09-19

Image under test:

```text
/media/freezer/SteamLibrary/vms/aspartame-build/artifacts/out/aspartame-2026.09.19-x86_64.iso
sha256: b9a03f6401a9c69641766090cc87c7379b648fcf7134d4262fb2a38366525ebb
```

The image was booted in a fresh QEMU system disk with a writable `/dev/vdb`
data disk and no `-virtfs` development share.

## Boot evidence

```text
IMAGE_VERSION=2026.09.19
/home/aspartame /dev/vdb ext4 rw
dev-share-not-mounted
python3 -m jarabe.main
/usr/lib/aspartame/gtk4-preview/venv/bin/python .../jarabe/main.py
Sugar Spaces ready: F7 = GTK3, F8 = GTK4
```

The persistent-home login profile was non-empty and both Spaces started from
the packaged image. The GTK4 root was `/usr/lib/aspartame/gtk4-preview`.

## Activity and reboot evidence

Calculate was launched through the GTK4 shell service. QEMU pointer events
pressed `7`, `*`, `6`, and `=`; the Activity displayed `42`. The Activity was
stopped through `org.laptop.Shell.StopActivity`, and the Journal payload was
stored as `7*6`.

The guest was rebooted through systemd. After the new boot, `/dev/vdb` was
mounted again, the development share remained absent, both shell processes
were present, and the exact payload was still present:

```text
/home/aspartame/.local/share/aspartame/gtk4/home/default/data/7cede992-dedd-4e7c-80af-2a07387b697d_n1n03uqe
7*6
```

This proves the packaged image can boot, start both Spaces, run and stop a
representative native Activity, and retain its Journal payload across reboot.
The broader manual Home/Frame/Journal/Settings interaction matrix remains
covered by the existing GTK4 runtime reports.
