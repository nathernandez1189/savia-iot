"""Rota solo la clave de demostración del ESP32, sin imprimirla.

Ejecutar en el servidor desde practica2/ tras la prueba en Wokwi.
"""

import os
import re
import secrets
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
env_path = root / ".env"
passwords = root / ".secrets" / "mosquitto_passwd"
original = env_path.read_text()
match = re.search(r"(?m)^MQTT_DEVICE_PASSWORD=([^\n]+)$", original)
if not match:
    raise SystemExit("No se encontró MQTT_DEVICE_PASSWORD en .env")
old = match.group(1)
new = secrets.token_hex(20)
subprocess.run(
    ["docker", "run", "--rm", "-v", f"{passwords.parent}:/work",
     "eclipse-mosquitto:2", "mosquitto_passwd", "-b", "/work/mosquitto_passwd",
     "savia_device", new],
    check=True, cwd=root, stdout=subprocess.DEVNULL,
)
temporary = env_path.with_suffix(".env.tmp")
temporary.write_text(original.replace("MQTT_DEVICE_PASSWORD=" + old,
                                      "MQTT_DEVICE_PASSWORD=" + new, 1))
os.chmod(temporary, 0o600)
temporary.replace(env_path)
subprocess.run(["docker", "compose", "restart", "mosquitto"], check=True, cwd=root,
               stdout=subprocess.DEVNULL)


def publish(password):
    return subprocess.run(
        ["docker", "compose", "exec", "-T", "mosquitto", "mosquitto_pub",
         "-h", "localhost", "-u", "savia_device", "-P", password,
         "-t", "invernadero1/temperatura", "-m", "24.0", "-q", "1"],
        cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        timeout=15,
    ).returncode


if publish(new) != 0 or publish(old) == 0:
    raise SystemExit("Rotación incompleta: comprobar broker y credenciales")
print("Clave del dispositivo rotada; nueva clave aceptada y anterior rechazada.")
