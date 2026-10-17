"""Savia IoT: servidor HTTP para lecturas del prototipo ESP32."""
import csv
import io
import json
import math
import os
import sqlite3
import threading
from datetime import datetime, timezone
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DATA_DIR = Path(os.getenv("SAVIA_DATA_DIR", Path(__file__).parent / "data"))
DB_KIND = os.getenv("SAVIA_DB_KIND", "sqlite").lower()
TOKEN = os.getenv("SAVIA_DEVICE_TOKEN", "")
MAX_BODY = 4096
FIELDS = ("received_at", "boot", "seq", "device_ts", "temperature", "humidity", "mode", "fan", "alarm", "reason")
LOCK = threading.Lock()


def connection():
    if DB_KIND == "sqlite":
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(DATA_DIR / "readings.sqlite3")
        db.row_factory = sqlite3.Row
        return db
    if DB_KIND == "postgres":
        import psycopg
        return psycopg.connect(os.environ["SAVIA_DATABASE_URL"])
    raise ValueError("SAVIA_DB_KIND debe ser sqlite o postgres")


def init_db():
    with closing(connection()) as db:
        if DB_KIND == "sqlite":
            db.execute("""CREATE TABLE IF NOT EXISTS readings (
                received_at TEXT NOT NULL, boot TEXT NOT NULL, seq INTEGER NOT NULL,
                device_ts INTEGER, temperature REAL NOT NULL, humidity REAL NOT NULL,
                mode TEXT NOT NULL, fan INTEGER NOT NULL, alarm TEXT NOT NULL,
                reason TEXT NOT NULL, PRIMARY KEY (boot, seq))""")
        else:
            db.execute("""CREATE TABLE IF NOT EXISTS readings (
                received_at TEXT NOT NULL, boot TEXT NOT NULL, seq BIGINT NOT NULL,
                device_ts BIGINT, temperature DOUBLE PRECISION NOT NULL,
                humidity DOUBLE PRECISION NOT NULL, mode TEXT NOT NULL,
                fan BOOLEAN NOT NULL, alarm TEXT NOT NULL, reason TEXT NOT NULL,
                PRIMARY KEY (boot, seq))""")
        db.commit()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rebuild_csv()


def rows(db, limit=None):
    sql = "SELECT " + ",".join(FIELDS) + " FROM readings ORDER BY received_at, boot, seq"
    if limit is not None:
        sql = "SELECT " + ",".join(FIELDS) + " FROM readings ORDER BY received_at DESC, boot DESC, seq DESC LIMIT " + str(limit)
    result = db.execute(sql)
    return [dict(zip(FIELDS, row)) for row in result.fetchall()]


def csv_bytes(data):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(data)
    return out.getvalue().encode("utf-8")


def rebuild_csv():
    with LOCK:
        with closing(connection()) as db:
            payload = csv_bytes(rows(db))
        temporary = DATA_DIR / "readings.csv.tmp"
        temporary.write_bytes(payload)
        temporary.replace(DATA_DIR / "readings.csv")


def parse_reading(value):
    if not isinstance(value, dict):
        raise ValueError("Se esperaba un objeto JSON")
    boot = value.get("boot")
    seq = value.get("seq")
    if not isinstance(boot, str) or not (1 <= len(boot) <= 64) or not boot.isalnum():
        raise ValueError("boot inválido")
    if type(seq) is not int or not 1 <= seq <= 2_147_483_647:
        raise ValueError("seq inválido")
    temperature, humidity = value.get("temperature"), value.get("humidity")
    if type(temperature) not in (int, float) or type(humidity) not in (int, float):
        raise ValueError("Se requieren temperatura y humedad numéricas")
    if not (math.isfinite(temperature) and math.isfinite(humidity)
            and -40 <= temperature <= 80 and 0 <= humidity <= 100):
        raise ValueError("Lectura fuera del rango del DHT22")
    mode = value.get("mode")
    if mode not in ("AUTO", "MANUAL") or type(value.get("fan")) is not bool:
        raise ValueError("Modo o ventilador inválido")
    ts = value.get("ts")
    if ts is not None and (type(ts) is not int or ts < 0):
        raise ValueError("ts inválido")
    alarm = str(value.get("alarm", "NORMAL"))[:32]
    reason = str(value.get("reason", "lectura"))[:64]
    return (datetime.now(timezone.utc).isoformat(), boot, seq, ts,
            float(temperature), float(humidity), mode, value["fan"], alarm, reason)


def save_reading(reading):
    placeholders = ",".join(["?" if DB_KIND == "sqlite" else "%s"] * len(FIELDS))
    sql = f"INSERT INTO readings ({','.join(FIELDS)}) VALUES ({placeholders}) ON CONFLICT (boot, seq) DO NOTHING"
    with closing(connection()) as db:
        result = db.execute(sql, reading)
        inserted = result.rowcount > 0
        db.commit()
    if inserted:
        rebuild_csv()
    return inserted


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, body, content_type="application/json; charset=utf-8"):
        payload = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        path = urlparse(self.path)
        if path.path == "/health":
            try:
                with closing(connection()) as db:
                    count = db.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
                return self.reply(200, {"status": "ok", "database": DB_KIND, "readings": count})
            except Exception:
                return self.reply(503, {"status": "database_unavailable"})
        if path.path == "/api/readings":
            limit = parse_qs(path.query).get("limit", ["100"])[0]
            if not limit.isdigit() or not 1 <= int(limit) <= 1000:
                return self.reply(400, {"error": "limit debe estar entre 1 y 1000"})
            with closing(connection()) as db:
                return self.reply(200, {"source": "ESP32_DHT22", "readings": rows(db, int(limit))})
        if path.path == "/api/readings.csv":
            with closing(connection()) as db:
                return self.reply(200, csv_bytes(rows(db)), "text/csv; charset=utf-8")
        self.reply(404, {"error": "Ruta no encontrada"})

    def do_POST(self):
        if urlparse(self.path).path != "/api/telemetry":
            return self.reply(404, {"error": "Ruta no encontrada"})
        if TOKEN and self.headers.get("X-Device-Token") != TOKEN:
            return self.reply(401, {"error": "Token del dispositivo inválido"})
        length = self.headers.get("Content-Length", "")
        if not length.isdigit() or not 0 < int(length) <= MAX_BODY:
            return self.reply(413, {"error": "JSON vacío o demasiado grande"})
        try:
            reading = parse_reading(json.loads(self.rfile.read(int(length))))
            inserted = save_reading(reading)
            self.reply(201 if inserted else 200, {"stored": True, "duplicate": not inserted,
                                                  "boot": reading[1], "seq": reading[2]})
        except (ValueError, json.JSONDecodeError) as exc:
            self.reply(400, {"error": str(exc)})
        except Exception:
            self.reply(503, {"error": "No se pudo guardar la lectura"})


def main():
    host = os.getenv("SAVIA_HOST", "127.0.0.1")
    if host not in ("127.0.0.1", "::1", "localhost") and not TOKEN:
        raise SystemExit("Defina SAVIA_DEVICE_TOKEN antes de publicar el servidor")
    init_db()
    port = int(os.getenv("SAVIA_PORT", "8000"))
    print(f"Savia IoT escuchando en http://{host}:{port}", flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
