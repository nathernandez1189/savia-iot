import csv
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).parent


class TelemetryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.port = 18931
        env = os.environ.copy()
        env.update(SAVIA_DATA_DIR=self.temp.name, SAVIA_PORT=str(self.port),
                   SAVIA_DEVICE_TOKEN="test-token", SAVIA_DB_KIND="sqlite")
        self.proc = subprocess.Popen([sys.executable, str(ROOT / "app.py")], env=env,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(50):
            try:
                self.request("GET", "/health")
                break
            except OSError:
                time.sleep(.05)
        else:
            self.fail("El servidor no inició")

    def tearDown(self):
        self.proc.terminate()
        self.proc.wait(timeout=3)
        self.temp.cleanup()

    def request(self, method, path, body=None, token=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["X-Device-Token"] = token
        data = None if body is None else json.dumps(body).encode()
        request = Request(f"http://127.0.0.1:{self.port}{path}", data=data,
                          headers=headers, method=method)
        try:
            with urlopen(request, timeout=2) as response:
                return response.status, response.read()
        except HTTPError as error:
            try:
                return error.code, error.read()
            finally:
                error.close()

    def test_dual_storage_auth_dedup_and_invalid_reading(self):
        sample = {"boot": "AB12CD34", "seq": 1, "ts": 1791633600000,
                  "temperature": 31.2, "humidity": 64.5, "mode": "AUTO",
                  "fan": True, "alarm": "NORMAL", "reason": "lectura"}
        self.assertEqual(self.request("POST", "/api/telemetry", sample)[0], 401)
        self.assertEqual(self.request("POST", "/api/telemetry", sample, "test-token")[0], 201)
        self.assertEqual(self.request("POST", "/api/telemetry", sample, "test-token")[0], 200)
        self.assertEqual(self.request("GET", "/health")[0], 200)
        self.assertEqual(json.loads(self.request("GET", "/health")[1])["readings"], 1)
        data = json.loads(self.request("GET", "/api/readings")[1])["readings"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["temperature"], 31.2)
        with open(Path(self.temp.name) / "readings.csv", newline="") as handle:
            lines = list(csv.DictReader(handle))
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["boot"], "AB12CD34")
        self.assertEqual(self.request("GET", "/api/readings.csv")[0], 200)
        self.assertEqual(self.request("POST", "/api/telemetry", {**sample, "seq": 2,
                         "temperature": None}, "test-token")[0], 400)
        self.assertEqual(json.loads(self.request("GET", "/health")[1])["readings"], 1)


if __name__ == "__main__":
    unittest.main()
