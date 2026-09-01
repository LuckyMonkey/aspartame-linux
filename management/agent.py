#!/usr/bin/env python3
"""Consent-visible device check-in client for Aspartame development."""
from __future__ import annotations
import argparse, json, os, platform, socket, urllib.request

def report():
    return {
        "hostname": socket.gethostname(),
        "os_version": "Aspartame development",
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "management_agent": "0.1.0",
    }

def main():
    parser = argparse.ArgumentParser(description="Send one visible Aspartame device check-in")
    parser.add_argument("--url", default="http://127.0.0.1:8787")
    parser.add_argument("--token", default=os.environ.get("ASPARTAME_MDM_TOKEN"))
    args = parser.parse_args()
    if not args.token:
        parser.error("provide --token or ASPARTAME_MDM_TOKEN")
    request = urllib.request.Request(
        args.url.rstrip("/") + "/api/v1/check-in",
        data=json.dumps(report()).encode(),
        headers={"Authorization": "Bearer " + args.token, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        print(response.read().decode())

if __name__ == "__main__":
    main()
