# GTK3/GTK4 headless runtime qualification — 2026-10-04

## Image

- ISO: `aspartame-2026.10.04-x86_64.iso`
- SHA-256: `742c849ac5bf55521a9e099a8234b0d1142451987fc5d379813e6807c1965cf7`
- QEMU: headless, QMP keyboard/tablet injection, SSH port `2223`
- GTK3 shell PID: `762`
- GTK4 shell PID: `1174`

## Results

The packaged GTK3 Help Activity completed three owned launch/stop cycles:

```text
cycle=1 service-ready=PASS cleanup=PASS
cycle=2 service-ready=PASS cleanup=PASS
cycle=3 service-ready=PASS cleanup=PASS
lifecycle-probe=PASS target=GTK3
```

The packaged GTK4 Help Activity completed three owned launch/activate/stop
cycles:

```text
cycle=1 service-ready=PASS shell-active=PASS cleanup=PASS
cycle=2 service-ready=PASS shell-active=PASS cleanup=PASS
cycle=3 service-ready=PASS shell-active=PASS cleanup=PASS
lifecycle-probe=PASS target=GTK4
```

The packaged Sugar health check returned:

```text
Sugar process PASS
Metacity PASS
org.laptop.Shell D-Bus PASS
Sugar Home X window PASS
Sugar import path PASS
Fatal shell log entries PASS
Result: PASS
```

The headless GTK3 Home input macro clicked the Classic search field and typed
`help`; the resulting screenshot shows the populated query and filtered Home
state: [qemu-gtk3-home-input.png](qemu-gtk3-home-input.png).

Together with the F7/F8 receipt in
`space-key-transport-20261004.md`, this closes the GTK3 shell launch/input/stop
and physical Space-selection evidence gates for the headless image.
