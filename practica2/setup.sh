#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ -e .env || -e .secrets/mosquitto_passwd ]]; then
  echo 'Ya hay configuración privada; no se sobreescribe. Para rotar, siga README.md.'
  exit 1
fi
mkdir -p .secrets
chmod 700 .secrets
python3 - <<'PY'
from pathlib import Path
from secrets import token_hex

device = token_hex(20)
collector = token_hex(20)
alerts = token_hex(20)
values = {
    'INFLUX_USER': 'savia_admin',
    'INFLUX_PASSWORD': token_hex(24),
    'INFLUX_ORG': 'savia',
    'INFLUX_BUCKET': 'invernadero',
    'INFLUX_TOKEN': token_hex(32),
    'GRAFANA_USER': 'admin',
    'GRAFANA_PASSWORD': token_hex(24),
    'MQTT_DEVICE_USER': 'savia_device',
    'MQTT_DEVICE_PASSWORD': device,
    'MQTT_COLLECTOR_USER': 'savia_collector',
    'MQTT_COLLECTOR_PASSWORD': collector,
    'MQTT_ALERT_USER': 'savia_alerts',
    'MQTT_ALERT_PASSWORD': alerts,
}
Path('.env').write_text(''.join(f'{key}={value}\n' for key, value in values.items()))
Path('.secrets/passwords.plain').write_text(f'savia_device:{device}\nsavia_collector:{collector}\nsavia_alerts:{alerts}\n')
PY
chmod 600 .env .secrets/passwords.plain
docker run --rm -v "$PWD/.secrets:/work" eclipse-mosquitto:2 mosquitto_passwd -U /work/passwords.plain
mv .secrets/passwords.plain .secrets/mosquitto_passwd
chmod 755 .secrets
chmod 644 .secrets/mosquitto_passwd
echo 'Configuración privada creada. No suba .env ni .secrets a GitHub.'
