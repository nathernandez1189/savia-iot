import csv
import json
import tempfile
import unittest
from pathlib import Path

from collector import Collector, line_protocol, parse_payload


def sample(seq=1, **changes):
    data = {"v": 2, "boot": "abc12345", "seq": seq, "temperature": 31.2,
            "humidity": 64.5, "mode": "AUTO", "fan": True,
            "alarm": "NORMAL", "reason": "lectura"}
    data.update(changes)
    return json.dumps(data).encode()


class CollectorTest(unittest.TestCase):
    def test_validation_and_line_protocol(self):
        row = parse_payload(sample())
        row["received_at_ms"] = 1000
        self.assertEqual(line_protocol(row),
                         "invernadero_aire,origen=wokwi,boot=abc12345 temperatura=31.2,humedad=64.5,secuencia=1i,ventilacion=1i 1000")
        for invalid in (sample(temperature=None), sample(humidity=105),
                        sample(seq=True), sample(boot="x,bad"), b"not-json"):
            with self.assertRaises((ValueError, TypeError)):
                parse_payload(invalid)

    def test_csv_dedup_and_influx_retry_after_restart(self):
        sent = []
        with tempfile.TemporaryDirectory() as directory:
            collector = Collector(directory, writer=lambda row: sent.append(row))
            self.assertTrue(collector.accept(sample(), received_at_ms=1000))
            self.assertFalse(collector.accept(sample(), received_at_ms=2000))
            self.assertTrue(collector.accept(sample(seq=2), received_at_ms=3000))
            with Path(directory, "readings.csv").open(newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual([(r["boot"], r["seq"], r["received_at_ms"]) for r in rows],
                             [("abc12345", "1", "1000"), ("abc12345", "2", "3000")])

            def unavailable(row):
                raise OSError("InfluxDB temporalmente caído")

            collector.writer = unavailable
            with self.assertRaises(OSError):
                collector.flush_pending()
            restarted = Collector(directory, writer=lambda row: sent.append(row))
            self.assertEqual(restarted.flush_pending(), 2)
            self.assertEqual(restarted.flush_pending(), 0)
            self.assertEqual([row["seq"] for row in sent], [1, 2])


if __name__ == "__main__":
    unittest.main()
