"""Apunta colector y Grafana a InfluxDB privado en otra VM.

Uso en la VM web: python3 configure_remote_influx.py 10.42.2.106
Obtiene el token cifrado desde SSM Parameter Store y no lo imprime.
"""

import ipaddress
import os
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen

if len(sys.argv) != 2:
    raise SystemExit("Uso: python3 configure_remote_influx.py IP_PRIVADA")
ip = ipaddress.ip_address(sys.argv[1])
if not ip.is_private:
    raise SystemExit("InfluxDB debe comunicarse por IP privada")
url = f"http://{ip}:8086"
with urlopen(url + "/health", timeout=5) as response:
    if response.status != 200:
        raise SystemExit("InfluxDB no está disponible")
token = subprocess.run(
    ["/usr/local/bin/aws", "ssm", "get-parameter", "--region", "us-east-1",
     "--name", "/savia/practica2/influx-token", "--with-decryption",
     "--query", "Parameter.Value", "--output", "text"],
    check=True, capture_output=True, text=True,
).stdout.strip()
if len(token) < 40:
    raise SystemExit("El token recuperado no es válido")
env_path = Path(__file__).parent / ".env"
original = env_path.read_text()
lines = [line for line in original.splitlines() if not line.startswith(("INFLUX_URL=", "INFLUX_TOKEN="))]
lines.extend((f"INFLUX_URL={url}", f"INFLUX_TOKEN={token}"))
backup = Path("/root/savia-practica2-env-before-remote-influx")
if not backup.exists():
    backup.write_text(original)
    os.chmod(backup, 0o600)
temporary = env_path.with_suffix(".env.tmp")
temporary.write_text("\n".join(lines) + "\n")
os.chmod(temporary, 0o600)
temporary.replace(env_path)
print(f"Colector y Grafana preparados para InfluxDB en {ip}; token no mostrado.")
