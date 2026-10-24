#!/usr/bin/env bash
# Prueba sintética de extremo a extremo. No sustituye la prueba del ESP32.
set -euo pipefail
cd "$(dirname "$0")"
set -a
# shellcheck disable=SC1091
source ./.env
set +a
boot="AWSCHECK$(date +%s)"
message=$(printf '{"v":2,"boot":"%s","seq":1,"temperature":31.2,"humidity":64.5,"mode":"AUTO","fan":true,"alarm":"NORMAL","reason":"prueba"}' "$boot")
docker compose exec -T mosquitto mosquitto_pub -h localhost -u "$MQTT_DEVICE_USER" -P "$MQTT_DEVICE_PASSWORD" -t invernadero1/telemetria -m "$message" -q 1
for attempt in $(seq 1 20); do
  if docker compose exec -T collector grep -q "$boot" /data/readings.csv; then
    break
  fi
  sleep 1
done
docker compose exec -T collector grep "$boot" /data/readings.csv
for attempt in $(seq 1 30); do
  if docker compose exec -T collector python -c 'import sqlite3,sys; db=sqlite3.connect("/data/outbox.sqlite3"); row=db.execute("SELECT sent FROM readings WHERE boot=?", (sys.argv[1],)).fetchone(); sys.exit(0 if row == (1,) else 1)' "$boot"; then
    break
  fi
  sleep 1
done
docker compose exec -T collector python -c 'import sqlite3,sys; db=sqlite3.connect("/data/outbox.sqlite3"); row=db.execute("SELECT sent FROM readings WHERE boot=?", (sys.argv[1],)).fetchone(); print("InfluxDB confirmado (sent=1):", row); sys.exit(0 if row == (1,) else 1)' "$boot"
docker compose exec -T influxdb influx query --org "$INFLUX_ORG" --token "$INFLUX_TOKEN" 'from(bucket: "'"$INFLUX_BUCKET"'") |> range(start: -10m) |> filter(fn: (r) => r.boot == "'"$boot"'")' | tail -n 5
printf 'ID de la prueba sintética: %s\n' "$boot"
