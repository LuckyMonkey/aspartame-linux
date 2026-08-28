# Networking

NetworkManager is the system authority in the bootstrap image. Avahi and
`nss-mdns` provide passive DNS-SD/mDNS discovery. Neighborhood 2.0 should
expose discovered services as objects and actions, not require protocol URLs.

Active scanning is a later explicit action only. It must never run
automatically on unknown, corporate, hotel, or public networks. VPN is a
future Sugar view with backend-neutral support for WireGuard, NetworkManager
VPN plugins, OpenVPN, and optionally Tailscale.

