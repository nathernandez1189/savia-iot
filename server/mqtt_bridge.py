"""Archiva en el servidor local las lecturas simuladas que publica Wokwi por MQTT.

El broker y el canal son públicos: esta integración es solo para la práctica.
La aplicación HTTP sigue siendo la única que valida y guarda cada lectura.
"""

import json
import logging
import os
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import paho.mqtt.client as mqtt


BROKER = os.getenv("SAVIA_MQTT_BROKER", "test.mosquitto.org")
TOPIC = os.getenv(
    "SAVIA_MQTT_TOPIC", "uao/invernadero/477744536654042113/v2/telemetry"
)
LOCAL_URL = "http://127.0.0.1:8000/api/telemetry"


def acceptable_payload(payload: bytes) -> bool:
    if len(payload) > 4096:
        return False
    try:
        reading = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False
    return isinstance(reading, dict) and reading.get("v") == 2


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        logging.warning("No se pudo conectar al broker: %s", reason_code)
        return
    client.subscribe(TOPIC, qos=0)
    logging.info("Suscrito al canal de telemetría del simulador")


def on_message(client, userdata, message):
    # El último valor del broker puede ser retenido; solo archivamos emisiones nuevas.
    if message.retain or not acceptable_payload(message.payload):
        return
    request = Request(
        LOCAL_URL,
        data=message.payload,
        headers={
            "Content-Type": "application/json",
            "X-Device-Token": os.environ["SAVIA_DEVICE_TOKEN"],
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=5) as response:
            result = json.load(response)
        logging.info(
            "Lectura %s/%s guardada (duplicada=%s)",
            result.get("boot"), result.get("seq"), result.get("duplicate"),
        )
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        logging.warning("Lectura no guardada: %s", error)


def main():
    if not os.getenv("SAVIA_DEVICE_TOKEN"):
        raise SystemExit("Falta SAVIA_DEVICE_TOKEN en el servidor")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                        client_id=f"savia-archive-{uuid.uuid4().hex[:12]}")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, 1883, keepalive=30)
    client.loop_forever(retry_first_connection=True)


if __name__ == "__main__":
    main()
