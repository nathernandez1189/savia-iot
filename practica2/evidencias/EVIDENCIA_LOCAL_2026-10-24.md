# Práctica 2: verificación local del 24 de octubre de 2026

**Proyecto:** Savia IoT, invernadero de tomates.
**Equipo:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés.
**Asignatura:** Inteligencia Artificial Aplicada a Internet de las Cosas.
**Docente:** Jhorman Andrés Villanueva Vivas.

## Alcance de esta prueba

Se inició en Docker Desktop una pila de cuatro servicios: Mosquitto, colector Python, InfluxDB OSS 2 y Grafana. Las lecturas se generaron con **un cliente MQTT de prueba en el computador**, con valores simulados de 31,2 °C y 32,5 °C y humedad relativa de 64,5 %. **Esta prueba local no demuestra que el ESP32 de Wokwi haya enviado datos al broker propio.** El despliegue posterior en AWS se documenta [por separado](EVIDENCIA_AWS_2026-10-24.md). El proyecto público de Wokwi de la Práctica 1 usa otra conexión y permanece separado.

## Resultados observados

1. `docker compose ps` mostró los cuatro servicios en estado `Up`. Tras la revisión final, los tres puertos del computador quedaron limitados a `127.0.0.1`: Mosquitto 1883, InfluxDB 8086 y Grafana 3000.
2. El cliente de prueba publicó dos mensajes autenticados en `invernadero1/telemetria` con identificador de arranque `PRACTICA2CHECK` y secuencias 1 y 2. El broker confirmó la publicación con QoS 1.
3. El colector registró las lecturas en `readings.csv` y en su cola local SQLite, y confirmó su escritura en InfluxDB. La consulta de InfluxDB devolvió la temperatura y humedad esperadas, con las etiquetas de arranque y secuencia.
4. La API de Grafana informó estado `ok`, reconoció la fuente `Savia InfluxDB` y el tablero `Savia IoT | Invernadero de tomates`. Una consulta del panel devolvió puntos de la serie de temperatura.
5. Grafana cargó la regla `savia-temp-alta`, el contacto MQTT `Savia MQTT` y la política de notificación. Tras superar 30 °C, la regla figuró como `firing` y `health ok`. Un suscriptor autenticado **recibió un mensaje de alerta** en `invernadero1/alertas`. Esto comprueba la notificación local, no una entrega por correo ni a un teléfono.
6. Las pruebas unitarias del colector pasaron: validación de lecturas y deduplicación/reintento de la cola. No se guardaron contraseñas ni tokens en el repositorio.

## Continuación realizada y evidencia académica

- El despliegue en AWS Academy ya se verificó; véase la [evidencia de AWS](EVIDENCIA_AWS_2026-10-24.md). Mantener InfluxDB y Grafana sin puertos públicos y retirar la apertura temporal de MQTT al terminar la demostración.
- La [copia pública de Wokwi](https://wokwi.com/projects/478779944323491841) ya envió lecturas a MQTT, CSV e InfluxDB de AWS con una clave temporal. El código compartido volvió a quedar sin credenciales y la clave se rotó; detalles en la [evidencia AWS](EVIDENCIA_AWS_2026-10-24.md).
- Guardar capturas legibles de AWS, Wokwi, tópicos, serie temporal, tablero y alerta recibida para la sustentación al grupo.
- Esta prueba local no acredita la topología de AWS. Posteriormente se instaló InfluxDB en una [segunda VM y subred pública](EVIDENCIA_AWS_2026-10-24.md), con acceso a 8086 restringido a la primera VM. PostgreSQL de la Práctica 1 permanece privado.

**Evolución de AWS:** la instancia existente `i-01f3188a0db02ef65` era `t3.micro` durante esta prueba local. Después se amplió a `t3.small`, se abrió MQTT temporalmente y se instaló la pila. La [evidencia posterior](EVIDENCIA_AWS_2026-10-24.md) prevalece para el estado en nube.

**Estado de entrega académica:** preparar los archivos y compartir el repositorio no equivale a subir la actividad en CampusDigital. El 24 de octubre se observó allí el cierre para el 31 de octubre de 2026 a las 12:00, hora de Colombia.
