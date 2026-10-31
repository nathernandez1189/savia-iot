# Práctica 2 | Implementación y checklist de entrega

**Asignatura:** Inteligencia Artificial Aplicada a Internet de las Cosas

**Docente:** Jhorman Andrés Villanueva Vivas

**Equipo:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés

**Evidencia técnica de referencia:** 24 de octubre de 2026

[Guía de ejecución](README.md) · [Evidencias](evidencias/README.md) · [Presentación](entregables.md)

## Caso de uso

Monitoreo de temperatura y humedad relativa del aire de un invernadero de tomates. El ESP32 simulado publica por MQTT y controla un LED que representa ventilación: encendido por encima de 30 °C, apagado por debajo de 27 °C e histéresis entre ambos límites. No hay sensor de suelo, ventilador físico ni modelo de IA entrenado.

## Implementación y evidencia disponible

| Componente | Implementación | Evidencia y alcance |
| --- | --- | --- |
| Dispositivo simulado | ESP32 + DHT22 + LED, con código en [wokwi/](wokwi/) | La [sesión AWS](evidencias/EVIDENCIA_AWS_2026-10-24.md) registró siete lecturas del arranque `39c72c8e`. El proyecto público conserva marcadores de credenciales. |
| Broker propio | Mosquitto, usuarios diferenciados y permisos por tópico | Se comprobó publicación autenticada. La evidencia registra rotación de la clave del dispositivo y rechazo de la anterior. |
| Colector | Validación y deduplicación por `boot` y `seq` | [collector.py](collector.py), [pruebas unitarias](test_collector.py) y lecturas observadas en los registros. |
| Persistencia | CSV, cola SQLite y base de series temporales InfluxDB | Las siete lecturas de Wokwi quedaron en CSV y produjeron catorce puntos de temperatura y humedad en InfluxDB. SQLite permite reintentos; Grafana consulta InfluxDB. |
| Separación de la base en AWS | Segunda EC2 Ubuntu y otra subred pública, con 8086 restringido al grupo de la primera EC2 | [Evidencia AWS](evidencias/EVIDENCIA_AWS_2026-10-24.md) y [plantilla CloudFormation](aws/influx-public-subnet.yaml). InfluxDB es autogestionada. |
| Visualización | Grafana con cuatro paneles: series y últimos valores de temperatura y humedad | [Captura AWS](evidencias/grafana-aws-2026-10-24.png). Incluye datos de Wokwi y del cliente de prueba; el último dato mostrado es sintético. |
| Notificación | Regla de temperatura superior a 30 °C y contacto MQTT | Se recibió una notificación de prueba y una automática en `invernadero1/alertas` en AWS. La automática se provocó con el dato sintético `AWSCHECK1792862155`. |
| Continuidad de la Práctica 1 | Servicios y base PostgreSQL independientes de esta pila | Durante la comprobación AWS, la aplicación anterior continuó respondiendo correctamente en `/health`. Es un resultado de esa sesión. |

Esta tabla resume la implementación y las evidencias; no sustituye la rúbrica del profesor ni confirma por sí sola una entrega o calificación.

## Antes de una nueva demostración

Marcar estas casillas al realizar la comprobación actual. Los resultados históricos no las completan automáticamente.

- [ ] Confirmar el laboratorio, la instancia, la IP vigente y los servicios necesarios.
- [ ] Revisar `docker compose ps`: cuatro servicios en local; en AWS con base separada, tres en la primera VM e InfluxDB en la segunda.
- [ ] Verificar la Práctica 1 en paralelo si ambas se van a exponer.
- [ ] Confirmar que la configuración privada existe y que no se muestra en la pantalla compartida.
- [ ] Preparar la simulación de la Práctica 2 con host y clave temporal de forma privada.
- [ ] Abrir Grafana y comprobar la fuente **Savia InfluxDB**. Elegir un intervalo reciente.
- [ ] Abrir el cliente MQTT con el usuario y tópico que permita la [ACL](mosquitto.acl). La cuenta `savia_device` solo publica.

## Recorrido que se muestra al profesor

| Paso | Qué mostrar | Cuándo se puede dar por comprobado |
| --- | --- | --- |
| 1. Sensor y control local | En Wokwi, subir a 32 °C y bajar a 26 °C | El LED cambia según la histéresis y el monitor serial muestra la temperatura. |
| 2. Comunicación | Monitor serial y mensaje en `invernadero1/telemetria` | Aparece una publicación nueva con temperatura, humedad, `boot` y `seq`. Conservar esos identificadores. |
| 3. Colector y CSV | Logs y últimas filas con los comandos de la [guía](README.md#3-mostrar-el-colector-la-base-y-grafana) | La misma lectura aparece en el CSV; no basta una fila de otra sesión. |
| 4. Base InfluxDB | `verify_influx.py` y consulta filtrada por `boot` y `seq` en Grafana Explore | Se recuperan de la base los valores de esa lectura. El script busca las últimas 24 horas. |
| 5. Gráficas | Tablero **Savia IoT \| Invernadero de tomates** | Los valores y la hora coinciden con la lectura observada. |
| 6. Alerta | Regla de Grafana y suscriptor de `invernadero1/alertas` | Se recibe la notificación. Distinguir una prueba del contacto de una alerta provocada por la regla. |

Si se usa `smoke_test.sh`, presentar su lectura como **dato sintético publicado por un cliente de prueba**. Su resultado no acredita que Wokwi esté conectado. El LED funciona localmente aun cuando falle MQTT.

## Evidencias para conservar

- [ ] Captura del circuito y monitor serial sin credenciales.
- [ ] Mensaje MQTT, fila CSV y consulta InfluxDB de la misma lectura nueva.
- [ ] Panel de Grafana con fecha e intervalo visibles.
- [ ] Regla y notificación recibida, identificando el origen del dato que la provocó.
- [ ] Topología y restricciones de acceso de AWS si se demuestra el despliegue en nube.
- [ ] Registrar fecha, entorno y limitaciones en una evidencia nueva; conservar las del 24 de octubre.

## Cierre y entrega académica

- [ ] Revisar la [presentación original](entregables.md) y contrastarla con la configuración vigente.
- [ ] Confirmar en CampusDigital los requisitos, plazo y estado de envío; confirmar aparte la exposición.
- [ ] Al terminar las pruebas del equipo, retirar la credencial temporal del simulador y rotarla con la herramienta indicada en la [guía](README.md#2-conectar-wokwi-al-broker-de-la-práctica-2).
- [ ] Revisar las aperturas temporales, recursos y presupuesto AWS con la persona responsable. No borrar volúmenes que contienen lecturas para resolver un problema de conexión.
