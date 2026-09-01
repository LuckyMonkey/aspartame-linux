#!/usr/bin/env python3
import json
import os
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

os.environ["ASPARTAME_ENROLLMENT_TOKEN"] = "test-enrollment"
with tempfile.TemporaryDirectory() as tmp:
    os.environ["ASPARTAME_MDM_DB"] = tmp + "/test.sqlite3"
    from server import Handler


class ManagementTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.host, cls.port = cls.httpd.server_address

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def request(self, method, path, body=None, headers=None):
        conn = HTTPConnection(self.host, self.port)
        conn.request(method, path, json.dumps(body).encode() if body else None, headers or {})
        response = conn.getresponse()
        return response.status, json.loads(response.read())

    def test_health_enroll_and_checkin(self):
        status, body = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")
        status, body = self.request("POST", "/api/v1/enroll", {"name": "test-laptop", "fingerprint": "abc", "os_version": "Aspartame dev"}, {"X-Enrollment-Token": "test-enrollment", "Content-Type": "application/json"})
        self.assertEqual(status, 201)
        token = body["token"]
        status, body = self.request("POST", "/api/v1/check-in", {"boot_completed": True}, {"Authorization": "Bearer " + token, "Content-Type": "application/json"})
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "accepted")


if __name__ == "__main__":
    unittest.main()
