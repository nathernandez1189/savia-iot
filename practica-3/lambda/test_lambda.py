"""Pruebas unitarias para la Lambda `FetchTelemetria` y el Motor de IA Agronómica."""

import json
import unittest

from lambda_function import (
    analyze_agronomic_ai,
    compute_vpd_and_dew_point,
    lambda_handler,
    records_to_csv,
)


class FakeTable:
    def __init__(self, items):
        self._items = items

    def query(self, **kwargs):
        return {"Items": list(self._items)}


class FakeIoTClient:
    def __init__(self):
        self.published = []

    def publish(self, **kwargs):
        self.published.append(kwargs)


class ServerlessLambdaTest(unittest.TestCase):
    def test_vpd_and_dew_point_physics(self):
        vpd, dew = compute_vpd_and_dew_point(25.0, 65.0)
        self.assertAlmostEqual(vpd, 1.11, delta=0.1)
        self.assertAlmostEqual(dew, 18.0, delta=0.5)

    def test_ai_predicts_thermal_stress_and_anomaly(self):
        base_ts = 1730680000000
        records = [
            {"device_id": "esp32_invernadero_01", "timestamp": base_ts + i * 60000, "temperatura": 27.0 + i * 0.4, "humedad": 65.0, "actuador_fan": False}
            for i in range(5)
        ]
        # Agregamos pico anómalo al final
        records.append({
            "device_id": "esp32_invernadero_01",
            "timestamp": base_ts + 5 * 60000,
            "temperatura": 31.8,
            "humedad": 55.0,
            "actuador_fan": True,
        })
        ai = analyze_agronomic_ai(records)
        self.assertEqual(ai["status"], "ALERTA")
        self.assertEqual(ai["ai_action"], "VENTILACION_ACTIVA_CRITICA")
        self.assertTrue(ai["anomaly_detected"])
        self.assertGreater(ai["temp_pred_15m"], 31.8)
        self.assertEqual(ai["minutes_to_stress_30c"], 0.0)

    def test_ai_detects_botrytis_risk(self):
        records = [
            {"device_id": "esp32_invernadero_01", "timestamp": 1730680000000, "temperatura": 21.0, "humedad": 92.0, "actuador_fan": False},
            {"device_id": "esp32_invernadero_01", "timestamp": 1730680060000, "temperatura": 21.2, "humedad": 93.0, "actuador_fan": False},
        ]
        ai = analyze_agronomic_ai(records)
        self.assertGreaterEqual(ai["botrytis_risk_pct"], 60)
        self.assertEqual(ai["ai_action"], "DESHUMIDIFICAR_BOTRYTIS")

    def test_lambda_get_sensor_and_csv_export(self):
        fake_table = FakeTable([
            {"device_id": "esp32_invernadero_01", "timestamp": 2000, "temperatura": 28.4, "humedad": 64.0, "actuador_fan": False},
            {"device_id": "esp32_invernadero_01", "timestamp": 1000, "temperatura": 28.0, "humedad": 65.0, "actuador_fan": False},
        ])
        res_json = lambda_handler({"httpMethod": "GET", "queryStringParameters": {"limit": "10"}}, table_resource=fake_table)
        self.assertEqual(res_json["statusCode"], 200)
        body = json.loads(res_json["body"])
        self.assertTrue(body["ok"])
        self.assertEqual(body["count"], 2)
        self.assertEqual(body["records"][0]["timestamp"], 1000)
        self.assertEqual(body["records"][1]["timestamp"], 2000)
        self.assertIn("vpd_kpa", body["ai"])

        res_csv = lambda_handler({"httpMethod": "GET", "queryStringParameters": {"format": "csv"}}, table_resource=fake_table)
        self.assertEqual(res_csv["statusCode"], 200)
        self.assertIn("text/csv", res_csv["headers"]["Content-Type"])
        self.assertIn("esp32_invernadero_01,1000,28.0,65.0,False", res_csv["body"])

    def test_lambda_post_actuador_publishes_mqtt(self):
        fake_iot = FakeIoTClient()
        event = {
            "httpMethod": "POST",
            "body": json.dumps({"device_id": "esp32_invernadero_01", "actuador_fan": True, "modo": "MANUAL"}),
        }
        res = lambda_handler(event, iot_client=fake_iot)
        self.assertEqual(res["statusCode"], 200)
        body = json.loads(res["body"])
        self.assertTrue(body["ok"])
        self.assertTrue(body["published_mqtt"])
        self.assertEqual(len(fake_iot.published), 1)
        self.assertEqual(fake_iot.published[0]["topic"], "invernadero1/actuador")


if __name__ == "__main__":
    unittest.main()
