#!/bin/bash
set -euo pipefail

useradd --create-home --shell /bin/bash aspartame
passwd --delete aspartame
printf 'root:freezer\n' | chpasswd
usermod --append --groups audio,video,storage,network,lp,wheel,uucp aspartame

systemctl enable NetworkManager.service
systemctl enable bluetooth.service
systemctl enable cups.service
systemctl enable avahi-daemon.service
systemctl enable systemd-timesyncd.service
systemctl enable sshd.service
systemd-machine-id-setup
ln -sfn /dev/null /etc/systemd/system/systemd-firstboot.service
ln -sfn /usr/share/zoneinfo/America/New_York /etc/localtime

install -d -o aspartame -g aspartame /home/aspartame/.config
install -o aspartame -g aspartame /etc/skel/.xinitrc /home/aspartame/.xinitrc
install -o aspartame -g aspartame /etc/skel/.bash_profile /home/aspartame/.bash_profile
install -d -o aspartame -g aspartame /home/aspartame/Desktop /home/aspartame/Downloads

install -d -m 0755 /mnt/aspartame-dev /usr/local/bin
cat > /usr/local/bin/aspartame-persistent-home <<'EOF'
#!/bin/sh
set -eu

device=/dev/vdb
for _ in 1 2 3 4 5 6 7 8 9 10; do
    test -b "$device" && break
    sleep 1
done
test -b "$device"

if ! blkid "$device" >/dev/null 2>&1; then
    mkfs.ext4 -F -L ASPARTAME_DATA "$device"
fi
mountpoint -q /home/aspartame || mount "$device" /home/aspartame
test "$(findmnt -n -o SOURCE --target /home/aspartame)" = "$device"
install -d -o aspartame -g aspartame /home/aspartame/Desktop \
    /home/aspartame/Downloads /home/aspartame/.config
if ! grep -qx 'exec /usr/local/bin/aspartame-x-session' /home/aspartame/.xinitrc 2>/dev/null; then
    if test -f /home/aspartame/.xinitrc && test ! -e /home/aspartame/.xinitrc.pre-aspartame-system-session; then
        cp -p /home/aspartame/.xinitrc /home/aspartame/.xinitrc.pre-aspartame-system-session
    fi
    install -o aspartame -g aspartame /etc/skel/.xinitrc /home/aspartame/.xinitrc
fi
if test ! -e /home/aspartame/.bash_profile; then
    install -o aspartame -g aspartame /etc/skel/.bash_profile \
        /home/aspartame/.bash_profile
fi
chown aspartame:aspartame /home/aspartame
EOF
chmod 0755 /usr/local/bin/aspartame-persistent-home
cat > /etc/systemd/system/aspartame-persistent-home.service <<'EOF'
[Unit]
Description=Mount Aspartame persistent user data
Requires=dev-vdb.device
After=dev-vdb.device local-fs.target
Before=graphical.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/aspartame-persistent-home
RemainAfterExit=yes

[Install]
WantedBy=local-fs.target
EOF
cat > /etc/systemd/system/aspartame-dev-share.service <<'EOF'
[Unit]
Description=Mount Aspartame host development share
Before=graphical.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/aspartame-dev-mount
RemainAfterExit=yes

[Install]
WantedBy=local-fs.target
EOF
# Install Aspartame Control Panel sections after pacman has installed Sugar.
# Keeping overrides out of the initial airootfs avoids file collisions with
# files owned by the current Arch sugar package.
chmod 0755 /usr/local/bin/aspartame-x-session
install -d /usr/share/sugar/extensions/cpsection
chmod 0755 /usr/local/libexec/aspartame-remove-activity
cp -a /usr/share/aspartame/cpsection/. /usr/share/sugar/extensions/cpsection/

# Install the pinned canonical Activity collection into the image.  The
# manifest is the single source of truth for these bundles.
install -d /usr/share/sugar/activities
while IFS=$'\t' read -r repo bundle; do
    test -n "$repo" || continue
    cp -a "/usr/share/aspartame/activities/$repo" \
        "/usr/share/sugar/activities/$bundle"
done < /usr/share/aspartame/activities/INSTALL-MANIFEST

site_packages=$(python3 -c 'import sugar3, os; print(os.path.dirname(sugar3.__file__))')
patch -d "$(dirname "$site_packages")" -p0 < \
    /usr/share/aspartame/0001-integrated-navigation.patch
install -D -m 0644 /usr/share/aspartame/select_a_thing.py \
    "$site_packages/jarabe/select_a_thing.py"
glib-compile-schemas /usr/share/glib-2.0/schemas
cat > /usr/local/bin/aspartame-session <<'EOF'
#!/bin/sh
set -eu
# The agent must start inside dbus-run-session so it registers on the same
# per-session bus used by Sugar and pkexec.
if test -x /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1; then
    /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1         >/tmp/aspartame-polkit-agent.log 2>&1 &
    polkit_agent_pid=$!
fi
sugar &
sugar_pid=$!
wait "$sugar_pid"
if test -n "${polkit_agent_pid:-}"; then
    kill "$polkit_agent_pid" 2>/dev/null || true
fi
EOF
chmod 0755 /usr/local/bin/aspartame-session
ln -sfn /usr/bin/fastfetch /usr/local/bin/neofetch
cat > /usr/local/bin/aspartame-dev-mount <<'EOF'
#!/bin/sh
set -eu
if ! mountpoint -q /mnt/aspartame-dev; then
    for _ in 1 2 3 4 5 6 7 8 9 10; do
        mount -t 9p -o trans=virtio,version=9p2000.L,msize=104857600 \
            aspartame-dev /mnt/aspartame-dev 2>/dev/null && break
        sleep 1
    done
fi
echo "Development share: /mnt/aspartame-dev"
EOF
chmod 0755 /usr/local/bin/aspartame-dev-mount

install -d -m 0755 /etc/ssh/sshd_config.d /etc/sudoers.d
cat > /usr/local/sbin/aspartame-start-sshd <<'EOF'
#!/bin/sh
set -eu
install -d -m 0755 /run/sshd
ssh-keygen -A
exec /usr/bin/sshd -D -e -f /etc/ssh/sshd_config
EOF
chmod 0755 /usr/local/sbin/aspartame-start-sshd
cat > /etc/sudoers.d/aspartame-ssh <<'EOF'
aspartame ALL=(root) NOPASSWD: /usr/bin/systemctl start aspartame-sshd.service, /usr/local/sbin/aspartame-start-sshd
EOF
chmod 0440 /etc/sudoers.d/aspartame-ssh
install -d -m 0755 /etc/ssh/sshd_config.d
cat > /etc/ssh/sshd_config.d/aspartame.conf <<'EOF'
ListenAddress 0.0.0.0
PermitRootLogin yes
PasswordAuthentication yes
AllowUsers root aspartame
EOF

cat > /etc/systemd/system/aspartame-sshd.service <<'EOF'
[Unit]
Description=Aspartame TCP SSH server
After=network.target
[Service]
Type=simple
ExecStartPre=/usr/bin/install -d -m 0755 /run/sshd
ExecStartPre=/usr/bin/ssh-keygen -A
ExecStartPre=/usr/bin/sshd -t
ExecStart=/usr/bin/sshd -D -e
Restart=on-failure
RestartSec=2
StandardOutput=journal+console
StandardError=journal+console

[Install]
WantedBy=multi-user.target graphical.target
EOF
systemctl preset-all || true
systemctl enable NetworkManager.service
systemctl disable sshd.socket sshd.service 2>/dev/null || true
systemctl mask sshd.socket 2>/dev/null || true
systemctl enable aspartame-sshd.service
systemctl enable aspartame-persistent-home.service aspartame-dev-share.service

# These diagnostics are part of the developer-facing image surface.  The
# profile copies regular files with conservative modes, so restore their
# executable bit explicitly in the final airootfs.
chmod 0755 \
    /usr/local/bin/aspartame-sugar-info \
    /usr/local/bin/aspartame-sugar-health \
    /usr/local/bin/aspartame-sugar-logs \
    /usr/local/bin/aspartame-sugar-state \
    /usr/local/bin/aspartame-sugar-imports \
    /usr/local/bin/aspartame-x-session \
    /usr/local/bin/aspartame-restart-sugar
