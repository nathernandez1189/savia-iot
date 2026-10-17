# Práctica 1 · Servidor web para Savia IoT

**Materia:** Inteligencia Artificial aplicada a Internet de las Cosas  
**Profesor:** Jhorman Andrés Villanueva Vivas  
**Caso:** monitoreo de temperatura y humedad del aire en un invernadero de tomates.

## Qué hace cada pieza

- **ESP32 + DHT22 en Wokwi:** produce lecturas simuladas de temperatura y humedad. Su lógica local enciende la ventilación simulada por encima de 30 °C y la apaga por debajo de 27 °C. Conserva el dashboard existente por MQTT.
- **Servidor Python en Ubuntu:** recibe `POST /api/telemetry`, valida los datos, evita duplicados y guarda cada lectura válida tanto en `readings.csv` como en la base de datos.
- **Base de datos:** SQLite para la comprobación local; PostgreSQL RDS en dos subredes privadas para AWS. La aplicación usa el mismo contrato HTTP en ambos casos.
- **Sitio Savia IoT publicado:** sigue siendo el dashboard existente. No debe confundirse con el servidor nuevo ni con la prueba de persistencia.

Los datos de Wokwi son **simulados**, no mediciones de un cultivo real. Open-Meteo, si aparece en el dashboard, describe estimaciones del clima exterior.

## 1. Prueba local del servidor

En un Ubuntu con Python 3, clonar el repositorio y ejecutar:

```bash
git clone https://github.com/nathernandez1189/savia-iot.git
cd savia-iot/server
mkdir -p data
SAVIA_HOST=0.0.0.0 SAVIA_DB_KIND=sqlite SAVIA_DATA_DIR="$PWD/data" SAVIA_DEVICE_TOKEN=CAMBIAR_ESTE_TOKEN python3 app.py
```

En otra terminal, usar una lectura de prueba. Sustituir el token por el valor elegido:

```bash
curl -i http://127.0.0.1:8000/api/telemetry \
  -H 'Content-Type: application/json' \
  -H 'X-Device-Token: CAMBIAR_ESTE_TOKEN' \
  -d '{"boot":"PRUEBA01","seq":1,"ts":1791633600000,"temperature":31.2,"humidity":64.5,"mode":"AUTO","fan":true,"alarm":"NORMAL","reason":"lectura"}'
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/readings?limit=10
```

La primera respuesta debe ser `201` y `stored:true`. Una repetición idéntica debe ser `200` y `duplicate:true`. `server/data/readings.csv` y `server/data/readings.sqlite3` deben existir; `health` debe indicar una lectura. Ejecutar `python3 -m unittest discover -s server -p 'test_*.py' -v` desde la raíz para verificar el almacenamiento dual.

**Wokwi no puede llamar a `localhost` de Ubuntu desde el navegador.** Para probar el flujo completo desde Wokwi se necesita una dirección alcanzable por internet, por ejemplo la IP elástica del servidor AWS. El `curl` anterior verifica el servidor local sin fingir que Wokwi ya está conectado.

## 2. Configurar el ESP32 para enviar al servidor

El archivo [`wokwi/sketch.ino`](wokwi/sketch.ino) conserva el envío MQTT al dashboard y agrega un envío HTTP con cola en RAM. Al principio del archivo, después de conocer la dirección pública del servidor, configurar:

```cpp
const char* API_URL="http://IP_ELASTICA/api/telemetry";
const char* API_TOKEN="TOKEN_PRIVADO_DEL_SERVIDOR";
```

Copiar esta versión del código al proyecto Wokwi, iniciar la simulación y mirar el monitor serial. Deben aparecer `HTTP guardado: #...` y, en el servidor, aumentar `readings`. Si se corta la red, el ESP32 conserva lecturas en su buffer temporal y reintenta; si se desborda, avisa por serial. Al reiniciar, ese buffer RAM se pierde. **No subir el token real al repositorio público.** El código publicado deja ambos campos vacíos deliberadamente.

## 3. Arquitectura AWS prevista

La plantilla [`aws/savia-iot.yaml`](aws/savia-iot.yaml) crea una VPC, una subred pública para Ubuntu, dos subredes privadas en zonas distintas para RDS PostgreSQL, una IP elástica y grupos de seguridad. HTTP 80 es público para el prototipo. SSH 22 se limita a la IP administradora; PostgreSQL 5432 solo acepta conexiones desde el servidor web. RDS no tiene acceso público. AWS puede cobrar por EC2, RDS, almacenamiento e IP elástica, incluso si el ejercicio no recibe tráfico.

Antes de crear la pila: elegir la región, identificar una **AMI Ubuntu Server 24.04 LTS amd64** de esa misma región, crear un par de claves EC2, conocer la IP pública administradora (`X.X.X.X/32`) y escoger una clave fuerte para RDS. En CloudFormation, cargar la plantilla y suministrar esos cuatro parámetros. No escribir claves en el repositorio. Revisar el costo estimado y la cuenta antes de confirmar la creación.

La pila crea la infraestructura, **pero no instala automáticamente el código ni inicia el servidor**. Una vez creada, usar el `WebIP` y `DatabaseHost` de las salidas. Conectarse al Ubuntu por SSH con el usuario `ubuntu` y la clave EC2 propia. Instalar y configurar:

```bash
sudo apt update
sudo apt install -y python3 python3-venv git nginx
sudo useradd --system --home /var/lib/savia-iot --shell /usr/sbin/nologin savia
sudo mkdir -p /opt/savia-iot /var/lib/savia-iot
sudo git clone https://github.com/nathernandez1189/savia-iot.git /opt/savia-iot
sudo python3 -m venv /opt/savia-iot/.venv
sudo /opt/savia-iot/.venv/bin/pip install 'psycopg[binary]>=3.2,<4'
sudo chown -R savia:savia /var/lib/savia-iot
sudo cp /opt/savia-iot/server/savia-iot.service /etc/systemd/system/
```

Crear `/etc/savia-iot.env` **en la instancia**, legible solo por root, con `SAVIA_HOST=127.0.0.1`, `SAVIA_PORT=8000`, `SAVIA_DB_KIND=postgres`, `SAVIA_DATA_DIR=/var/lib/savia-iot`, `SAVIA_DATABASE_URL=postgresql://saviaadmin:CLAVE_RDS@HOST_RDS:5432/saviaiot` y `SAVIA_DEVICE_TOKEN=TOKEN_PRIVADO`. Si la contraseña contiene caracteres especiales de URL, codificarlos en la URL. Después:

```bash
sudo chmod 600 /etc/savia-iot.env
sudo systemctl daemon-reload
sudo systemctl enable --now savia-iot
sudo systemctl status savia-iot --no-pager
```

Configurar Nginx para publicar el puerto 80 y pasar peticiones al puerto 8000 local. Archivo `/etc/nginx/sites-available/savia-iot`:

```nginx
server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Activarlo con `sudo ln -s /etc/nginx/sites-available/savia-iot /etc/nginx/sites-enabled/savia-iot`, quitar el sitio predeterminado, comprobar `sudo nginx -t` y reiniciar Nginx. La URL `http://IP_ELASTICA/health` debe responder `status:ok` y `database:postgres`. Luego configurar el ESP32 y comprobar en `/api/readings`, CSV y PostgreSQL. El HTTP sin TLS de una IP elástica sirve para la demostración académica con datos simulados; para uso real se requiere dominio y HTTPS.

## Evidencias que exige la práctica

1. Captura de Wokwi con ESP32, DHT22 y monitor serial donde se vea el envío exitoso.
2. Respuesta de `/health` y `/api/readings` en local y luego en AWS.
3. Archivo CSV con filas de lecturas; consulta de la tabla `readings` en SQLite local y PostgreSQL RDS.
4. AWS VPC/subred pública para EC2, subredes privadas para RDS, IP elástica y grupos de seguridad (sin mostrar claves).
5. Repositorio GitHub actualizado y presentación breve del flujo, resultados y límites.

La entrega se considera completa cuando el equipo verifica lecturas **reales de la simulación** en CSV y base de datos local **y** en AWS; la existencia del dashboard o de la plantilla por sí sola no demuestra esa persistencia.

## Apagar después de la sustentación

La plantilla toma una instantánea de RDS al borrar la pila. Esa instantánea puede seguir generando costos: revisar y borrar manualmente solo cuando se haya conservado lo necesario. Verificar también que no quede una IP elástica sin asociar. Antes de crear o eliminar recursos, revisar la cuenta y las condiciones de cobro vigentes de AWS.
