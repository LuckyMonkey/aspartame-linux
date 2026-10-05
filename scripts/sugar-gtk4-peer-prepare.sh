#!/usr/bin/env bash
set -euo pipefail

# Prepare one disposable headless GTK4 guest for a two-peer Salut fixture.
# This only changes the explicitly private fixture NIC and creates a fresh
# Sugar profile path; it does not alter the normal GTK4 profile or management
# network.

if ! grep -qx 'IMAGE_ID=aspartame' /etc/os-release; then
    echo 'This helper is guest-only; run it inside the Aspartame VM.' >&2
    exit 2
fi
if [ "$(id -u)" -ne 0 ]; then
    echo 'Run this helper as root so it can configure the fixture NIC.' >&2
    exit 2
fi

peer=${1:-}
interface=${ASPARTAME_PEER_INTERFACE:-enp0s2}
case "$peer" in
    a)
        address=10.77.0.1
        hostname=arch-peer-a
        profile_name=AspartamePeerA
        ;;
    b)
        address=10.77.0.2
        hostname=arch-peer-b
        profile_name=AspartamePeerB
        ;;
    *)
        echo "usage: $0 a|b" >&2
        exit 2
        ;;
esac

case "$interface" in
    enp0s2) ;;
    *) echo "refusing to configure non-fixture interface: $interface" >&2; exit 2 ;;
esac

ip -4 addr flush dev "$interface"
ip link set "$interface" up
ip -4 addr add "$address/24" dev "$interface"

# The image intentionally has no static /etc/hostname.  Hostnamed gives
# Avahi/Salut a distinct service name without touching the management NIC.
busctl call org.freedesktop.hostname1 /org/freedesktop/hostname1 \
    org.freedesktop.hostname1 SetHostname sb "$hostname" true
busctl call org.freedesktop.hostname1 /org/freedesktop/hostname1 \
    org.freedesktop.hostname1 SetStaticHostname sb "$hostname" true

run_id=$(date -u +%Y%m%dT%H%M%SZ)-$$
sugar_home="/home/aspartame/.sugar/peers/$peer-$run_id"
env_file="/run/aspartame-peer-$peer.env"
install -d -o aspartame -g aspartame "$sugar_home"
umask 077
{
    printf 'export ASPARTAME_SUGAR_HOME=%q\n' "$sugar_home"
    printf 'export ASPARTAME_SUGAR_PROFILE=default\n'
    printf 'export ASPARTAME_SUGAR_PROFILE_NAME=%q\n' "$profile_name"
} > "$env_file"
chown aspartame:aspartame "$env_file"

systemctl restart avahi-daemon

echo "peer-fixture=READY peer=$peer address=$address hostname=$hostname"
echo "peer-fixture-env=$env_file"
echo "source $env_file before starting scripts/sugar-gtk4-run.sh as aspartame"
ip -brief addr show dev "$interface"
