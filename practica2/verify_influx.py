"""Consulta InfluxDB desde la VM por un identificador de arranque observado.

Uso: python3 verify_influx.py 39c72c8e
Lee el token privado de .env; nunca lo imprime.
"""

import csv
import io
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

if len(sys.argv) != 2 or not re.fullmatch(r"[A-Za-z0-9]{1,64}", sys.argv[1]):
    raise SystemExit("Uso: python3 verify_influx.py BOOT_ALFANUMERICO")
boot = sys.argv[1]
config = dict(line.split("=", 1) for line in (Path(__file__).parent / ".env").read_text().splitlines() if "=" in line)
flux = (f'from(bucket: "{config["INFLUX_BUCKET"]}") |> range(start: -24h) '
        f'|> filter(fn: (r) => r.boot == "{boot}" and '
        '(r._field == "temperatura" or r._field == "humedad"))')
url = config.get("INFLUX_URL", "http://127.0.0.1:8086").rstrip("/") + "/api/v2/query?" + urlencode({"org": config["INFLUX_ORG"]})
request = Request(url, data=flux.encode(), method="POST", headers={
    "Authorization": "Token " + config["INFLUX_TOKEN"],
    "Content-Type": "application/vnd.flux",
    "Accept": "application/csv",
})
with urlopen(request, timeout=15) as response:
    raw = response.read().decode()
reader = csv.reader(io.StringIO(raw))
header = None
found = []
for row in reader:
    if not row or row[0].startswith("#"):
        continue
    if "_field" in row and "_value" in row:
        header = row
        continue
    if header and len(row) == len(header):
        record = dict(zip(header, row))
        found.append((record.get("_field"), record.get("_value"), record.get("_time")))
if not found:
    raise SystemExit(f"Sin puntos en InfluxDB para {boot}")
print(json.dumps({"boot": boot, "puntos": len(found), "muestra": found[-4:]}, ensure_ascii=False))
