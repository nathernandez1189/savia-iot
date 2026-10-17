# Savia IoT · práctica 1 en Azure

**Materia:** Inteligencia Artificial aplicada a Internet de las Cosas  
**Docente:** Jhorman Andrés Villanueva Vivas  
**Caso de uso:** monitoreo de temperatura y humedad del aire en un invernadero de tomates.

> **Antes de entregar:** el enunciado permite una máquina virtual en la nube, pero el criterio de evaluación nombra expresamente **AWS** y pide una **IP elástica** y **grupos de seguridad**. Azure ofrece una arquitectura equivalente con **IP pública estática** y **grupo de seguridad de red (NSG)**, pero no es literalmente AWS. Conviene confirmar con el docente que acepta Azure. La plantilla AWS original se conserva en [`aws/savia-iot.yaml`](aws/savia-iot.yaml) por si exige esa plataforma.

## Estado comprobado y alcance

- El servidor Python recibió datos de prueba y los guardó en CSV y SQLite. Pasó la prueba automatizada de autenticación, deduplicación y validación.
- El proyecto Wokwi con ESP32 y DHT22 compiló y siguió emitiendo lecturas por MQTT al dashboard. El código HTTP está listo, pero su URL permanece vacía hasta que exista un servidor público.
- Se creó el grupo **vacío** `rg-savia-iot-practica1`; no contiene la VM ni la base de datos.
- La plantilla Bicep compiló sin errores. Azure validó la arquitectura en `northcentralus` con VM `Standard_B2als_v2` y la vista previa mostró **11 recursos por crear**. Las pruebas en `eastus2` (política regional) y con `Standard_B1s` (sin capacidad en las regiones probadas) fallaron.
- **Todavía no se ha comprobado un envío Wokwi → servidor ni se ha desplegado la aplicación en Azure.** No se deben presentar esas partes como terminadas.

La telemetría de Wokwi es simulada. El DHT22 mide temperatura y humedad relativa del **aire**; no mide suelo ni nutrientes.

## Arquitectura Azure propuesta

```text
Wokwi / ESP32 / DHT22
         │ HTTP POST
         ▼
IP pública estática → VM Ubuntu en subred pública → CSV local
                                      │
                                      └── PostgreSQL Flexible Server
                                          en subred privada delegada
```

La plantilla [`azure/main.bicep`](azure/main.bicep) define una red virtual, subred pública para Ubuntu, subred privada delegada para PostgreSQL Flexible Server, zona DNS privada, IP pública estática y NSG. El NSG permite HTTP 80 y limita SSH 22 a la IP administradora. La base de datos tiene acceso público deshabilitado. **La plantilla crea recursos facturables**: VM, disco, IP pública y PostgreSQL, entre otros. El precio depende de región, suscripción, créditos y tiempo de uso.

## Antes de crear recursos

1. Iniciar sesión en [portal.azure.com](https://portal.azure.com/) con la cuenta académica prevista y verificar la suscripción. No seleccionar una suscripción de trabajo.
2. Consultar el costo y el crédito **antes** de crear los 11 recursos. El 17 de octubre de 2026, la [API pública de precios de Azure](https://prices.azure.com/api/retail/prices) indicaba en `northcentralus` USD 0,0376/h para la VM Linux `Standard_B2als_v2`, USD 0,017/h para PostgreSQL B1ms y USD 0,115/GB-mes para su almacenamiento. A 720 horas y 32 GB, el subtotal es **USD 43,0/mes**, sin disco de VM, IP pública, transferencia ni posibles cargos de backup. Las tarifas pueden cambiar; verificar el costo aplicable a la suscripción antes de desplegar.
3. Tener una clave pública SSH. En el equipo de Natalia existe `~/.ssh/id_ed25519.pub`; usar únicamente el contenido del archivo `.pub`, nunca la clave privada.
4. Conocer la IP pública desde la cual se administrará la VM y escribirla como `X.X.X.X/32`. Si esa IP cambia, habrá que actualizar la regla SSH del NSG.
5. Elegir una contraseña nueva y privada para PostgreSQL. No escribirla en el repositorio ni en mensajes del grupo.

## Despliegue con Azure Cloud Shell

Cloud Shell tiene Azure CLI y Bicep. Tras confirmar la cobertura de costos, abrir Cloud Shell desde el portal. El grupo de recursos `rg-savia-iot-practica1` ya existe y está vacío. La región de los recursos de la plantilla es `northcentralus`; puede diferir de la región del grupo. Descargar la plantilla publicada en GitHub:

```bash
curl -fL -o main.bicep https://raw.githubusercontent.com/nathernandez1189/savia-iot/main/azure/main.bicep
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

Solo después de revisar esa vista previa y los costos, ejecutar `az deployment group create` con los mismos parámetros. Guardar los valores de salida `webPublicIp` y `postgresHost`. La VM todavía necesita instalar la aplicación.

## Instalar Savia IoT en la VM

Entrar por SSH como `azureuser` usando la IP pública. En Ubuntu:

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

Activar el sitio, retirar el predeterminado, validar con `sudo nginx -t` y recargar Nginx. `http://IP_PUBLICA/health` debe responder con `status:ok` y `database:postgres`. El HTTP sin TLS es solo para datos simulados de la práctica; para uso real se necesita HTTPS.

## Conectar Wokwi y verificar la entrega

En el `sketch.ino` del proyecto Wokwi, definir `API_URL="http://IP_PUBLICA/api/telemetry"` y `API_TOKEN="TOKEN_PRIVADO_LARGO"` con el mismo token de la VM; guardar e iniciar la simulación. **No publicar el token en GitHub.** Se espera `HTTP guardado: #...` en el monitor serial. Confirmar que aumenta el número de `readings` en `/health`, que `/api/readings` muestra la lectura y que `/api/readings.csv` contiene el mismo valor. La tabla `readings` debe aparecer en PostgreSQL; la conexión a esta base solo debe funcionar desde la VM.

Para exponer, mostrar: circuito ESP32/DHT22, programa modificado, lectura del monitor serial, servidor local con CSV+SQLite, servidor Azure con CSV+PostgreSQL, red pública/privada, IP estática, NSG y enlace del repositorio. Señalar que el control de ventilación permanece local en el ESP32.

## Cierre y costos

Una VM detenida desde dentro de Ubuntu puede seguir facturando. Al terminar, confirmar en el portal si se deben conservar o eliminar VM, PostgreSQL, disco, IP pública y copias de seguridad. Antes de borrar el grupo de recursos, guardar el CSV y cualquier evidencia de la práctica. La eliminación es irreversible para los datos que no se hayan respaldado.

## Fuentes de arquitectura

- [Microsoft Learn: PostgreSQL Flexible Server con acceso privado](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-networking-private)
- [Microsoft Learn: VM Ubuntu con Bicep](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/quick-create-bicep)
- [Microsoft Learn: IP pública estándar y estática](https://learn.microsoft.com/en-us/azure/templates/microsoft.network/2024-03-01/publicipaddresses)
