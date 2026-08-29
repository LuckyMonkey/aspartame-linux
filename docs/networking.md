# Networking

NetworkManager is the system authority in the bootstrap image. Avahi and
`nss-mdns` provide passive DNS-SD/mDNS discovery. Neighborhood 2.0 should
expose discovered services as objects and actions, not require protocol URLs.

The Sugar desktop toolbar now provides an explicit `Scan network` action. It
derives the active guest IPv4 subnet and runs `nmap -sn -T3` with a 45-second
limit, presenting results in a dialog. It never scans automatically. In the
QEMU reference setup this discovers the private `10.0.2.0/24` user-mode NAT
network; bridged networking will be needed to discover the physical LAN.
Active scanning must remain an explicit action on unknown, corporate, hotel,
or public networks. VPN is a
future Sugar view with backend-neutral support for WireGuard, NetworkManager
VPN plugins, OpenVPN, and optionally Tailscale.

