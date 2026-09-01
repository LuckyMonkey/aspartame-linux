# Aspartame Management Plane

This is the first management-plane slice for Aspartame. It is deliberately
separate from Sugar and runs locally during development.

Current capabilities:

- health endpoint
- one-time device enrollment
- hashed device bearer tokens
- device status check-ins
- policy readout
- installed Activity catalog readout
- audit events

It does **not** provide arbitrary remote shell, arbitrary command execution,
silent package removal, or hidden surveillance.

## Run

```bash
python3 -m management.server --bind 127.0.0.1 --port 8787
```

Then open <http://127.0.0.1:8787/health> or run:

```bash
curl http://127.0.0.1:8787/health
```

Set `ASPARTAME_ENROLLMENT_TOKEN` before starting the server to control device
enrollment. The default is intentionally unusable for real deployment.

## API

```text
GET  /health
POST /api/v1/enroll
GET  /api/v1/device
POST /api/v1/check-in
GET  /api/v1/policy
GET  /api/v1/catalog
```

The enrollment response contains the device token once. Store it securely.
The server stores only its SHA-256 hash.

This first slice uses a small SQLite database and Python's standard library so
it can be demonstrated immediately on a clean Arch development image. A
Django adapter can be added later without changing the API or data model.
