# Práctica 1 · Savia IoT en AWS Academy Learner Lab

**Materia:** Inteligencia Artificial Aplicada a Internet de las Cosas  
**Docente:** Jhorman Andrés Villanueva Vivas  
**Equipo:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés  
**Caso:** monitoreo de temperatura y humedad del aire en un invernadero de tomates.

## Qué se construyó

El [ESP32 y DHT22 simulados en Wokwi](https://wokwi.com/projects/477744536654042113) publican lecturas por MQTT. El servicio `server/mqtt_bridge.py` instalado en una VM Ubuntu de AWS recibe ese canal y envía las lecturas a `server/app.py` dentro de la misma máquina. La aplicación valida y deduplica los mensajes y guarda cada registro tanto en PostgreSQL RDS como en `readings.csv`.

```text
Wokwi (ESP32 + DHT22) → MQTT público → puente en Ubuntu → aplicación web
                                              ├→ PostgreSQL RDS privado
                                              └→ CSV local
```

La regla de ventilación continúa en el ESP32: en AUTO se activa sobre 30 °C y se desactiva bajo 27 °C. El LED representa el actuador; no es un ventilador físico. La [página de demostración](https://nathernandez1189.github.io/savia-iot/) conserva su historial, controles y clima exterior de Open-Meteo; ese clima exterior no sustituye datos del DHT22.

**Seguridad:** el proyecto Wokwi y este repositorio son públicos. El token de la aplicación no está en el código del ESP32; se conserva solo en la VM mediante AWS Systems Manager Parameter Store. El broker público de pruebas no autentica el origen de la telemetría, por lo que se usa únicamente con datos simulados.

## AWS que quedó desplegado

En `us-east-1`, la pila de CloudFormation **`savia-iot-lab`** creó la VPC, la subred pública con Ubuntu EC2, dos subredes privadas para PostgreSQL RDS, una IP elástica y grupos de seguridad. RDS no tiene acceso público; su puerto 5432 acepta conexiones solo desde el grupo de la VM. La plantilla está en [`aws/savia-iot.yaml`](aws/savia-iot.yaml). La instancia usa el perfil `LabInstanceProfile` del Learner Lab; para otra cuenta AWS hay que ajustar ese perfil y comprobar límites/costos.

El servidor está en [`http://184.193.138.254/`](http://184.193.138.254/) mientras la pila permanezca activa. Las rutas de comprobación son [`/health`](http://184.193.138.254/health), [`/api/readings?limit=10`](http://184.193.138.254/api/readings?limit=10) y [`/api/readings.csv`](http://184.193.138.254/api/readings.csv). La portada, `/health` y `/api/readings` abrieron en el navegador interno durante la verificación del 24 de octubre. Chrome de esa sesión bloqueó HTTP; un bloqueo del cliente no prueba que la VM esté caída. No hay HTTPS configurado en esta instalación.

El 24 de octubre de 2026 se verificó `status=ok`, `database=postgres`, y que el contador subió de 4 a 13 durante la simulación. Los últimos registros `boot=465479e7`, `seq=23…25`, `24.0 °C`, `65.0 %` aparecieron en la API y en el CSV. En una segunda sesión del mismo día, el control local de Wokwi funcionó, pero la pasarela Wi-Fi `wss://netwi.wokwi.com/` falló en dos navegadores: no se generaron lecturas nuevas en AWS. Para la demostración, iniciar Wokwi con anticipación y confirmar `RED=OK` y un contador creciente antes de afirmar que el flujo completo está activo. La evidencia detallada está en [`entregables/Evidencia_AWS_2026-10-24.md`](entregables/Evidencia_AWS_2026-10-24.md).

## Reproducir la primera parte en Ubuntu local

Una prueba en macOS o los tests con SQLite por sí solos no sustituyen la instalación local de Ubuntu pedida en el enunciado. En una máquina o contenedor Ubuntu con Python 3:

```bash
git clone https://github.com/nathernandez1189/savia-iot.git
cd savia-iot
python3 -m unittest discover -s server -p 'test_*.py' -v
mkdir -p server/data
SAVIA_HOST=127.0.0.1 SAVIA_DB_KIND=sqlite SAVIA_DATA_DIR="$PWD/server/data" SAVIA_DEVICE_TOKEN=TOKEN_DE_PRUEBA python3 server/app.py
```

Desde otra terminal, enviar una muestra de prueba, sustituir el token de ejemplo y revisar las dos salidas:

```bash
curl -i http://127.0.0.1:8000/api/telemetry -H 'Content-Type: application/json' -H 'X-Device-Token: TOKEN_DE_PRUEBA' -d '{"boot":"PRUEBA01","seq":1,"ts":1791633600000,"temperature":31.2,"humidity":64.5,"mode":"AUTO","fan":true,"alarm":"NORMAL","reason":"lectura"}'
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/readings.csv
```

Esta petición manual verifica el servidor local; para afirmar que Wokwi entregó lecturas a esa instalación haría falta un puente MQTT local o una dirección pública alcanzable desde Wokwi. Fotografiar o capturar la ejecución y las filas de `server/data/readings.csv` y `server/data/readings.sqlite3`.

## Cómo mostrar la práctica

1. Iniciar [Wokwi](https://wokwi.com/projects/477744536654042113) y variar el DHT22.
2. Mostrar monitor serial, modo AUTO y LED. Una secuencia mayor de 30 °C debe encenderlo; una menor de 27 °C debe apagarlo.
3. Abrir `/health`, `/api/readings` y `/api/readings.csv`; comparar `boot`, `seq`, temperatura y humedad.
4. En AWS CloudFormation mostrar los 16 recursos de la pila; en RDS, comprobar que la base no es pública. No mostrar credenciales ni parámetros secretos.
5. Explicar que los datos son simulados y que el MQTT público es una limitación de seguridad.

## Cierre del laboratorio y costos

La estudiante fijó un máximo de USD 15 para el laboratorio. La eliminación de la pila está programada para el **1 de noviembre de 2026 a las 23:00, hora de Bogotá**; otra programación retira dos parámetros privados después. La programación no impide por sí sola que se gaste saldo antes de esa fecha. Verificar el presupuesto y el estado de ambas programaciones en AWS antes de la exposición y confirmar posteriormente que la pila y sus recursos se eliminaron. La plantilla de esta instalación usa `DeletionPolicy: Delete` para que RDS no deje una instantánea facturable al cerrar.

## Alcance

Se verificó una demostración de reglas y telemetría simulada, no un cultivo real ni un modelo de IA entrenado. Aún debe completarse y capturarse una instalación **local separada en Ubuntu** si el docente exige evidencia de esa primera fase. La presentación y la subida al campus son acciones del equipo, no se deducen de este repositorio.
