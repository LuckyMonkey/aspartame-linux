#!/usr/bin/env python3
"""Small localhost-first Aspartame management service."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("ASPARTAME_MDM_DB", ROOT / "runtime" / "aspartame-mdm.sqlite3"))
ENROLLMENT_TOKEN = os.environ.get("ASPARTAME_ENROLLMENT_TOKEN", "change-me-before-enrollment")
VERSION = "0.1.0"


def now():
    return datetime.now(timezone.utc).isoformat()


def db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            fingerprint TEXT NOT NULL UNIQUE,
            os_version TEXT NOT NULL DEFAULT '',
            token_hash TEXT NOT NULL,
            last_seen TEXT,
            last_report TEXT NOT NULL DEFAULT '{}',
            enabled INTEGER NOT NULL DEFAULT 1,
            enrolled_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            action TEXT NOT NULL,
            details TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL
        );
    """)
    return connection


def audit(connection, device_id, action, details=None):
    connection.execute("INSERT INTO audit(device_id, action, details, created_at) VALUES (?, ?, ?, ?)",
                       (device_id, action, json.dumps(details or {}), now()))
    connection.commit()


def device_from_request(handler):
    header = handler.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    digest = hashlib.sha256(header[7:].encode()).hexdigest()
    connection = db()
    row = connection.execute("SELECT * FROM devices WHERE token_hash = ? AND enabled = 1", (digest,)).fetchone()
    connection.close()
    return row


class Handler(BaseHTTPRequestHandler):
    server_version = "AspartameMDM/" + VERSION

    def send_json(self, status, value):
        payload = json.dumps(value, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def body(self):
        length = int(self.headers.get("Content-Length", "0"))
        try:
            return json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return None

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            return self.send_json(200, {"service": "aspartame-mdm", "status": "ok", "version": VERSION})
        row = device_from_request(self)
        if row is None:
            return self.send_json(401, {"error": "authentication required"})
        connection = db()
        if path == "/api/v1/device":
            result = {"id": row["id"], "name": row["name"], "os_version": row["os_version"],
                      "last_seen": row["last_seen"], "enabled": bool(row["enabled"])}
        elif path == "/api/v1/policy":
            result = {"name": "default", "allowed_activity_ids": [], "hidden_activity_ids": [],
                      "notes": "No remote actions are enabled in this development profile."}
        elif path == "/api/v1/catalog":
            catalog_path = os.environ.get("ASPARTAME_ACTIVITY_CATALOG")
            result = {"activities": []}
            if catalog_path and Path(catalog_path).exists():
                result = {"activities": json.loads(Path(catalog_path).read_text())}
        else:
            connection.close()
            return self.send_json(404, {"error": "not found"})
        audit(connection, row["id"], "read:" + path)
        connection.close()
        self.send_json(200, result)

    def do_POST(self):
        path = urlparse(self.path).path
        data = self.body()
        if data is None:
            return self.send_json(400, {"error": "request body must be JSON"})
        if path == "/api/v1/enroll":
            if self.headers.get("X-Enrollment-Token") != ENROLLMENT_TOKEN:
                return self.send_json(403, {"error": "invalid enrollment token"})
            name, fingerprint = data.get("name"), data.get("fingerprint")
            if not name or not fingerprint:
                return self.send_json(400, {"error": "name and fingerprint are required"})
            connection = db()
            if connection.execute("SELECT 1 FROM devices WHERE fingerprint = ?", (fingerprint,)).fetchone():
                connection.close()
                return self.send_json(409, {"error": "device already enrolled"})
            device_id, token = secrets.token_hex(16), secrets.token_urlsafe(32)
            connection.execute("INSERT INTO devices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                               (device_id, name, fingerprint, data.get("os_version", ""),
                                hashlib.sha256(token.encode()).hexdigest(), None, "{}", 1, now()))
            audit(connection, device_id, "enroll", {"name": name})
            connection.close()
            return self.send_json(201, {"device_id": device_id, "token": token, "warning": "token is shown once"})
        row = device_from_request(self)
        if row is None:
            return self.send_json(401, {"error": "authentication required"})
        if path != "/api/v1/check-in":
            return self.send_json(404, {"error": "not found"})
        connection = db()
        connection.execute("UPDATE devices SET last_seen = ?, last_report = ?, os_version = ? WHERE id = ?",
                           (now(), json.dumps(data), data.get("os_version", row["os_version"]), row["id"]))
        audit(connection, row["id"], "check-in", {"keys": sorted(data)})
        connection.commit()
        connection.close()
        self.send_json(200, {"status": "accepted", "next_check_in_seconds": 300})

    def log_message(self, format, *args):
        print("[mdm] " + format % args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    print(f"Aspartame MDM {VERSION} listening on http://{args.bind}:{args.port}")
    ThreadingHTTPServer((args.bind, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
