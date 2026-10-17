# Savia IoT · práctica 1 en Azure

**Materia:** Inteligencia Artificial aplicada a Internet de las Cosas  
**Docente:** Jhorman Andrés Villanueva Vivas  
**Caso de uso:** monitoreo de temperatura y humedad del aire en un invernadero de tomates.

> **Plataforma acordada:** según la confirmación de la estudiante, el docente acepta Azure para esta práctica. El criterio escrito nombra **AWS**, **IP elástica** y **grupos de seguridad**; en Azure se documentarán sus equivalentes funcionales: **IP pública estática** y **grupo de seguridad de red (NSG)**. La plantilla AWS original se conserva en [`aws/savia-iot.yaml`](aws/savia-iot.yaml) como referencia.

## Estado comprobado y alcance

- El 17 de octubre de 2026 quedó desplegado el grupo `rg-savia-iot-practica1` en **Azure for Students**, con VM Ubuntu `savia-web`, IP pública estática `23.101.172.173`, PostgreSQL Flexible Server privado y NSG. La aplicación responde en [http://23.101.172.173/health](http://23.101.172.173/health).
- El ESP32 simulado en [Wokwi](https://wokwi.com/projects/477744536654042113) publica temperatura y humedad por el canal MQTT de pruebas que ya usa el dashboard. Un puente ejecutado en la VM recibe ese canal y entrega cada lectura a la aplicación web local, que la valida y la guarda en PostgreSQL y CSV. **No se añadió ningún token al código público de Wokwi.**
- Se verificó la sesión de Wokwi `a4cb5ad6`: el monitor serial mostró la lectura `#6` de **24,0 °C y 65,0 %**, y el mismo identificador y valores aparecieron en PostgreSQL y en `readings.csv`. El endpoint público `/api/readings` también devolvió lecturas de esa sesión.
- Las pruebas automatizadas de validación, autenticación, deduplicación, doble almacenamiento y filtro del puente MQTT pasaron en la VM. La sesión demuestra funcionamiento puntual; no constituye una prueba de disponibilidad prolongada.
- Se configuró una alerta presupuestal. **La alerta no detiene los cobros**; la infraestructura se conservará solo hasta la clase del **24 de octubre de 2026** y deberá retirarse tras respaldar las evidencias.

La telemetría de Wokwi es simulada. El DHT22 mide temperatura y humedad relativa del **aire**; no mide suelo ni nutrientes.

## Arquitectura Azure desplegada

```text
Wokwi / ESP32 / DHT22 ── MQTT público de pruebas ──► VM Ubuntu
                                                     │ puente MQTT
                                                     ▼
IP pública estática ── HTTP 80 ──► aplicación web ──► CSV local
                                      │
                                      └── PostgreSQL Flexible Server
                                          en subred privada delegada
```

La plantilla [`azure/main.bicep`](azure/main.bicep) define una red virtual, subred pública para Ubuntu, subred privada delegada para PostgreSQL Flexible Server, zona DNS privada, IP pública estática y NSG. El NSG permite HTTP 80 y limita SSH 22 a la IP administradora. La base de datos tiene acceso público deshabilitado. **Estos recursos son facturables**: VM, disco, IP pública y PostgreSQL, entre otros. El precio depende de región, suscripción, créditos y tiempo de uso.

## Preparación del despliegue realizado

1. Iniciar sesión en [portal.azure.com](https://portal.azure.com/) con la cuenta académica prevista y verificar la suscripción. No seleccionar una suscripción de trabajo.
2. Consultar el costo y el crédito **antes** de crear los 11 recursos. El 17 de octubre de 2026, la [API pública de precios de Azure](https://prices.azure.com/api/retail/prices) indicaba en `northcentralus` USD 0,0376/h para la VM Linux `Standard_B2als_v2`, USD 0,017/h para PostgreSQL B1ms y USD 0,115/GB-mes para su almacenamiento. A 720 horas y 32 GB, el subtotal es **USD 43,0/mes**, sin disco de VM, IP pública, transferencia ni posibles cargos de backup. Las tarifas pueden cambiar; verificar el costo aplicable a la suscripción antes de desplegar.
3. Tener una clave pública SSH. En el equipo de Natalia existe `~/.ssh/id_ed25519.pub`; usar únicamente el contenido del archivo `.pub`, nunca la clave privada.
4. Conocer la IP pública desde la cual se administrará la VM y escribirla como `X.X.X.X/32`. Si esa IP cambia, habrá que actualizar la regla SSH del NSG.
5. Elegir una contraseña nueva y privada para PostgreSQL. No escribirla en el repositorio ni en mensajes del grupo.

## Despliegue con Azure Cloud Shell

Cloud Shell tiene Azure CLI y Bicep. El despliegue ya se completó; estas instrucciones permiten reproducirlo en otra suscripción, previa revisión de costos. La región de los recursos es `northcentralus`; puede diferir de la región del grupo. Descargar la plantilla publicada en GitHub:

```bash
curl -fL -o main.bicep https://raw.githubusercontent.com/nathernandez1189/savia-iot/0a4f2c7f64197d02acdd9dbf2bacebe9265407c0/azure/main.bicep
```

Comprobar que `az account show` indica la suscripción prevista. Completar los parámetros en Cloud Shell sin incluir claves privadas ni contraseñas en el historial:

```bash
read -r -p 'IP administradora (X.X.X.X/32): ' SAVIA_ADMIN_CIDR
read -r -p 'Clave publica SSH: ' SAVIA_SSH_PUB
read -r -s -p 'Contrasena PostgreSQL: ' SAVIA_DB_PASSWORD
```

Antes de ejecutar el despliegue, validar la plantilla y revisar el cambio propuesto:

```bash
az bicep build --file main.bicep
az deployment group validate --resource-group rg-savia-iot-practica1 --template-file main.bicep --parameters location=northcentralus vmSize=Standard_B2als_v2 adminIpCidr="$SAVIA_ADMIN_CIDR" sshPublicKey="$SAVIA_SSH_PUB" dbPassword="$SAVIA_DB_PASSWORD"
az deployment group what-if --resource-group rg-savia-iot-practica1 --template-file main.bicep --parameters location=northcentralus vmSize=Standard_B2als_v2 adminIpCidr="$SAVIA_ADMIN_CIDR" sshPublicKey="$SAVIA_SSH_PUB" dbPassword="$SAVIA_DB_PASSWORD"
```

Solo después de revisar esa vista previa, confirmar los costos y preparar una IP administradora y una clave SSH **reales**, ejecutar:

```bash
az deployment group create --resource-group rg-savia-iot-practica1 --template-file main.bicep --parameters location=northcentralus vmSize=Standard_B2als_v2 adminIpCidr="$SAVIA_ADMIN_CIDR" sshPublicKey="$SAVIA_SSH_PUB" dbPassword="$SAVIA_DB_PASSWORD"
```

Guardar los valores de salida `webPublicIp` y `postgresHost`. Los parámetros temporales usados para la validación no sirven para un despliegue real.

## Instalar Savia IoT en la VM

Entrar por SSH como `azureuser` usando la IP pública. En Ubuntu:

```bash
sudo apt update
sudo apt install -y python3 python3-venv git nginx
sudo useradd --system --home /var/lib/savia-iot --shell /usr/sbin/nologin savia
sudo mkdir -p /opt/savia-iot /var/lib/savia-iot
sudo git clone https://github.com/nathernandez1189/savia-iot.git /opt/savia-iot
sudo python3 -m venv /opt/savia-iot/.venv
sudo /opt/savia-iot/.venv/bin/pip install -r /opt/savia-iot/server/requirements.txt
sudo chown -R savia:savia /var/lib/savia-iot
sudo cp /opt/savia-iot/server/savia-iot.service /etc/systemd/system/
```

Crear `/etc/savia-iot.env` en la VM, legible solo por root:

```text
SAVIA_HOST=127.0.0.1
SAVIA_PORT=8000
SAVIA_DB_KIND=postgres
SAVIA_DATA_DIR=/var/lib/savia-iot
SAVIA_DATABASE_URL=postgresql://saviaadmin:CONTRASENA_CODIFICADA@HOST_POSTGRES:5432/saviaiot?sslmode=require
SAVIA_DEVICE_TOKEN=TOKEN_PRIVADO_LARGO
```

Sustituir `HOST_POSTGRES` por la salida `postgresHost`. Si la contraseña contiene caracteres especiales de URL, codificarlos en la URL. El token del dispositivo debe ser privado y distinto de la contraseña de la base de datos. Luego:

```bash
sudo chmod 600 /etc/savia-iot.env
sudo systemctl daemon-reload
sudo systemctl enable --now savia-iot
sudo systemctl status savia-iot --no-pager
```

Crear `/etc/nginx/sites-available/savia-iot`:

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

Activar el sitio, retirar el predeterminado, validar y recargar Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/savia-iot /etc/nginx/sites-enabled/savia-iot
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

`http://IP_PUBLICA/health` debe responder con `status:ok` y `database:postgres`. El HTTP sin TLS es solo para datos simulados de la práctica; para uso real se necesita HTTPS.

## Conexión de Wokwi y verificación de la entrega

El proyecto Wokwi ya publica en el canal `uao/invernadero/477744536654042113/v2/telemetry` del broker público de pruebas. El archivo [`server/mqtt_bridge.py`](server/mqtt_bridge.py) se instala como el servicio `savia-mqtt` de la VM. Este se suscribe al canal, ignora mensajes retenidos o malformados y envía cada lectura a la aplicación web en `127.0.0.1:8000/api/telemetry`. La aplicación valida, deduplica y escribe en PostgreSQL y CSV. El token queda **solo en la VM** y no se publica en Wokwi ni en GitHub.

Para reproducir esa integración en una VM recién creada, instalar las dependencias de [`server/requirements.txt`](server/requirements.txt), copiar [`server/savia-mqtt.service`](server/savia-mqtt.service) a `/etc/systemd/system/`, activar `savia-mqtt` y comprobar sus registros con `journalctl -u savia-mqtt`. Iniciar Wokwi y contrastar el `boot`, `seq`, temperatura y humedad del monitor serial con [las lecturas públicas](http://23.101.172.173/api/readings) y [el CSV](http://23.101.172.173/api/readings.csv).

El broker MQTT es **público y no autentica el origen del dato**: otra persona podría publicar en el mismo canal. Por ello estas lecturas son evidencia de una simulación académica, no mediciones confiables de un cultivo real. El HTTP de la IP pública tampoco tiene TLS; no enviar datos sensibles por este prototipo.

Para exponer, mostrar: circuito ESP32/DHT22, programa modificado, lectura del monitor serial, servidor local con CSV+SQLite, servidor Azure con CSV+PostgreSQL, red pública/privada, IP estática, NSG y enlace del repositorio. Señalar que el control de ventilación permanece local en el ESP32.

## Cierre y costos

Una VM detenida desde dentro de Ubuntu puede seguir facturando. Al terminar, confirmar en el portal si se deben conservar o eliminar VM, PostgreSQL, disco, IP pública y copias de seguridad. Antes de borrar el grupo de recursos, guardar el CSV y cualquier evidencia de la práctica. La eliminación es irreversible para los datos que no se hayan respaldado.

## Fuentes de arquitectura

- [Microsoft Learn: PostgreSQL Flexible Server con acceso privado](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-networking-private)
- [Microsoft Learn: VM Ubuntu con Bicep](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/quick-create-bicep)
- [Microsoft Learn: IP pública estándar y estática](https://learn.microsoft.com/en-us/azure/templates/microsoft.network/2024-03-01/publicipaddresses)
