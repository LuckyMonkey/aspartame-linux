#!/bin/bash
set -euo pipefail

useradd --create-home --shell /bin/bash aspartame
passwd --delete aspartame
printf 'root:freezer\n' | chpasswd
usermod --append --groups audio,video,storage,network,lp,wheel aspartame

systemctl enable NetworkManager.service
systemctl enable bluetooth.service
systemctl enable cups.service
systemctl enable avahi-daemon.service
systemctl enable systemd-timesyncd.service

install -d -o aspartame -g aspartame /home/aspartame/.config
install -o aspartame -g aspartame /etc/skel/.xinitrc /home/aspartame/.xinitrc
install -o aspartame -g aspartame /etc/skel/.bash_profile /home/aspartame/.bash_profile
install -d -o aspartame -g aspartame /home/aspartame/Desktop /home/aspartame/Downloads

rm -f /etc/systemd/system/getty@tty1.service.d/autologin.conf
systemctl preset-all || true
