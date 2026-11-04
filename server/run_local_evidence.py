"""Script de prueba automatizada para generar evidencia local de la Práctica 1."""
import subprocess
import time
import json
import urllib.request
import sqlite3
import os
import sys
from pathlib import Path

server_dir = Path(__file__).resolve().parent
data_dir = (server_dir / "data").resolve()
data_dir.mkdir(parents=True, exist_ok=True)

for f in data_dir.glob("*"):
    try:
        f.unlink()
    except Exception:
        pass

env = os.environ.copy()
env["SAVIA_HOST"] = "127.0.0.1"
env["SAVIA_PORT"] = "8000"
env["SAVIA_DB_KIND"] = "sqlite"
env["SAVIA_DATA_DIR"] = str(data_dir)
env["SAVIA_DEVICE_TOKEN"] = "token_secreto_practica1"

proc = subprocess.Popen([sys.executable, str(server_dir / "app.py")], env=env)
time.sleep(1.5)

try:
    print(">>> 1. Health check inicial:")
    with urllib.request.urlopen("http://127.0.0.1:8000/health") as resp:
        print(f"Status: {resp.status} | Body: {resp.read().decode().strip()}")

    print("\n>>> 2. Enviando lecturas de prueba simulando el ESP32...")
    samples = [
        {"boot": "a4cb5ad6", "seq": 1, "ts": 1792458000000, "temperature": 24.5, "humidity": 65.0, "mode": "AUTO", "fan": False, "alarm": "NORMAL", "reason": "lectura"},
        {"boot": "a4cb5ad6", "seq": 2, "ts": 1792458005000, "temperature": 31.0, "humidity": 63.0, "mode": "AUTO", "fan": True, "alarm": "NORMAL", "reason": "lectura"},
        {"boot": "a4cb5ad6", "seq": 3, "ts": 1792458010000, "temperature": 32.0, "humidity": 45.0, "mode": "AUTO", "fan": True, "alarm": "BAJA", "reason": "lectura"},
        # Lectura repetida (seq 3) para probar deduplicación
        {"boot": "a4cb5ad6", "seq": 3, "ts": 1792458010000, "temperature": 32.0, "humidity": 45.0, "mode": "AUTO", "fan": True, "alarm": "BAJA", "reason": "lectura"},
        {"boot": "a4cb5ad6", "seq": 4, "ts": 1792458015000, "temperature": 28.0, "humidity": 60.0, "mode": "MANUAL", "fan": False, "alarm": "NORMAL", "reason": "remoto"}
    ]

    for i, s in enumerate(samples, 1):
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/telemetry",
            data=json.dumps(s).encode("utf-8"),
            headers={"Content-Type": "application/json", "X-Device-Token": "token_secreto_practica1"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode().strip()
            print(f"  Envio #{i} (seq={s['seq']}): HTTP {resp.status} -> {body}")

    print("\n>>> 3. Health check tras envios:")
    with urllib.request.urlopen("http://127.0.0.1:8000/health") as resp:
        print(f"Status: {resp.status} | Body: {resp.read().decode().strip()}")

    print("\n>>> 4. Consultando API de lecturas (/api/readings?limit=5):")
    with urllib.request.urlopen("http://127.0.0.1:8000/api/readings?limit=5") as resp:
        api_data = json.loads(resp.read().decode("utf-8"))
        print(f"Total lecturas devueltas: {len(api_data['readings'])}")
        for r in api_data["readings"]:
            print(f"  Seq: {r['seq']} | Temp: {r['temperature']}C | Hum: {r['humidity']}% | Fan: {r['fan']} | Alarm: {r['alarm']} | Mode: {r['mode']}")

    csv_path = data_dir / "readings.csv"
    print("\n>>> 5. Verificacion del archivo CSV (server/data/readings.csv):")
    print(f"Ruta: {csv_path}")
    print("Contenido:")
    print(csv_path.read_text(encoding="utf-8").strip())

    db_path = data_dir / "readings.sqlite3"
    print("\n>>> 6. Verificacion de la Base de Datos (server/data/readings.sqlite3):")
    print(f"Ruta: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT received_at, boot, seq, temperature, humidity, mode, fan, alarm, reason FROM readings ORDER BY seq ASC")
    rows = cur.fetchall()
    print(f"Total registros en tabla 'readings': {len(rows)}")
    for r in rows:
        print(f"  {r}")
    conn.close()

finally:
    proc.terminate()
    proc.wait()
