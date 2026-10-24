"""Recibe telemetría MQTT y la conserva en CSV e InfluxDB OSS 2.x.

SQLite funciona como cola local para reintentar escrituras a InfluxDB sin
perder una lectura cuando la base temporalmente no responde.
"""

import csv
import io
import json
import logging
import math
import os
import sqlite3
import threading
import time
import uuid
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

FIELDS = ("received_at_ms", "boot", "seq", "temperature", "humidity", "mode", "fan", "alarm", "reason")
TOPIC = "invernadero1/telemetria"


def parse_payload(payload: bytes):
    if len(payload) > 4096:
        raise ValueError("mensaje demasiado grande")
    data = json.loads(payload)
    if not isinstance(data, dict) or data.get("v") != 2:
        raise ValueError("versión de telemetría incorrecta")
    boot, seq = data.get("boot"), data.get("seq")
    if not isinstance(boot, str) or not boot.isalnum() or not 1 <= len(boot) <= 64:
        raise ValueError("identificador de arranque inválido")
    if type(seq) is not int or not 1 <= seq <= 2_147_483_647:
        raise ValueError("secuencia inválida")
    temp, humidity = data.get("temperature"), data.get("humidity")
    if type(temp) not in (int, float) or type(humidity) not in (int, float):
        raise ValueError("temperatura o humedad ausente")
    if not math.isfinite(temp) or not math.isfinite(humidity) or not -40 <= temp <= 80 or not 0 <= humidity <= 100:
        raise ValueError("lectura fuera del rango del DHT22")
    mode, fan = data.get("mode"), data.get("fan")
    if mode not in ("AUTO", "MANUAL") or type(fan) is not bool:
        raise ValueError("estado de control inválido")
    alarm, reason = data.get("alarm", "NORMAL"), data.get("reason", "lectura")
    if not isinstance(alarm, str) or not isinstance(reason, str) or len(alarm) > 32 or len(reason) > 64:
        raise ValueError("evento inválido")
    return {"boot": boot, "seq": seq, "temperature": float(temp), "humidity": float(humidity),
            "mode": mode, "fan": int(fan), "alarm": alarm, "reason": reason}


def line_protocol(row):
    # boot se validó como alfanumérico; ninguna etiqueta recibe datos libres.
    return (f'invernadero_aire,origen=simulacion,boot={row["boot"]} '
            f'temperatura={row["temperature"]},humedad={row["humidity"]},'
            f'secuencia={row["seq"]}i,ventilacion={row["fan"]}i '
            f'{row["received_at_ms"]}')


def send_influx(row):
    query = urlencode({"org": os.environ["INFLUX_ORG"], "bucket": os.environ["INFLUX_BUCKET"], "precision": "ms"})
    request = Request(
        f'{os.environ["INFLUX_URL"].rstrip("/")}/api/v2/write?{query}',
        data=line_protocol(row).encode(), method="POST",
        headers={"Authorization": "Token " + os.environ["INFLUX_TOKEN"],
                 "Content-Type": "text/plain; charset=utf-8"},
    )
    with urlopen(request, timeout=5) as response:
        if response.status != 204:
            raise RuntimeError(f"InfluxDB respondió {response.status}")


class Collector:
    def __init__(self, data_dir, writer=send_influx):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.database = self.data_dir / "outbox.sqlite3"
        self.csv_path = self.data_dir / "readings.csv"
        self.writer = writer
        self.lock = threading.RLock()
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS readings (
                received_at_ms INTEGER NOT NULL, boot TEXT NOT NULL, seq INTEGER NOT NULL,
                temperature REAL NOT NULL, humidity REAL NOT NULL, mode TEXT NOT NULL,
                fan INTEGER NOT NULL, alarm TEXT NOT NULL, reason TEXT NOT NULL,
                sent INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(boot, seq))""")
        self.export_csv()

    def connect(self):
        return sqlite3.connect(self.database)

    def export_csv(self):
        with self.lock, self.connect() as db:
            rows = db.execute("SELECT " + ",".join(FIELDS) + " FROM readings ORDER BY received_at_ms,boot,seq").fetchall()
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(FIELDS)
            writer.writerows(rows)
            temporary = self.csv_path.with_suffix(".csv.tmp")
            temporary.write_text(output.getvalue(), encoding="utf-8")
            temporary.replace(self.csv_path)

    def accept(self, payload: bytes, received_at_ms=None):
        row = parse_payload(payload)
        row["received_at_ms"] = int(received_at_ms if received_at_ms is not None else time.time() * 1000)
        with self.lock, self.connect() as db:
            result = db.execute(
                "INSERT OR IGNORE INTO readings (" + ",".join(FIELDS) + ") VALUES (?,?,?,?,?,?,?,?,?)",
                tuple(row[field] for field in FIELDS),
            )
            inserted = result.rowcount == 1
        if inserted:
            self.export_csv()
        return inserted

    def flush_pending(self):
        count = 0
        with self.lock, self.connect() as db:
            db.row_factory = sqlite3.Row
            pending = db.execute("SELECT " + ",".join(FIELDS) + " FROM readings WHERE sent=0 ORDER BY received_at_ms,boot,seq LIMIT 100").fetchall()
            for raw in pending:
                row = dict(raw)
                self.writer(row)
                db.execute("UPDATE readings SET sent=1 WHERE boot=? AND seq=?", (row["boot"], row["seq"]))
                db.commit()
                count += 1
        return count


def main():
    import paho.mqtt.client as mqtt

    required = ("MQTT_HOST", "MQTT_USER", "MQTT_PASSWORD", "INFLUX_URL", "INFLUX_ORG", "INFLUX_BUCKET", "INFLUX_TOKEN")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise SystemExit("Faltan variables: " + ", ".join(missing))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    collector = Collector(os.getenv("DATA_DIR", "/data"))
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="savia-collector-" + uuid.uuid4().hex[:12])
    client.username_pw_set(os.environ["MQTT_USER"], os.environ["MQTT_PASSWORD"])

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            logging.error("No se pudo autenticar el colector: %s", reason_code)
        else:
            client.subscribe(TOPIC, qos=1)
            logging.info("Suscrito a %s", TOPIC)

    def on_message(client, userdata, message):
        if message.retain:
            return
        try:
            inserted = collector.accept(message.payload)
            if inserted:
                logging.info("Lectura recibida y guardada en CSV")
        except (ValueError, UnicodeError, json.JSONDecodeError) as error:
            logging.warning("Lectura descartada: %s", error)
        except OSError:
            logging.exception("No se pudo guardar la lectura localmente")

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect_async(os.environ["MQTT_HOST"], int(os.getenv("MQTT_PORT", "1883")), keepalive=30)
    client.loop_start()
    try:
        while True:
            try:
                n = collector.flush_pending()
                if n:
                    logging.info("%d lecturas enviadas a InfluxDB", n)
            except Exception:
                logging.exception("InfluxDB no disponible; se reintentará sin perder el CSV")
            time.sleep(5)
    finally:
        client.loop_stop()


if __name__ == "__main__":
    main()
