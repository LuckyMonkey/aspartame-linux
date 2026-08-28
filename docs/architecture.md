# Aspartame architecture

Aspartame is an Arch Linux live image built by `archiso`. Sugar is the primary
session, launched by an autologin on tty1 through Xorg and `startx`. The
underlying system remains ordinary Arch: systemd, NetworkManager, pacman,
normal home directories, and a real shell remain available.

The first profile intentionally uses upstream Arch packages. Aspartame-owned
changes belong in the archiso profile or future PKGBUILDs, not in a fork of
Sugar or systemd.

