# Práctica 2: verificación local del 24 de octubre de 2026

**Proyecto:** Savia IoT, invernadero de tomates.
**Equipo:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés.
**Asignatura:** Inteligencia Artificial Aplicada a Internet de las Cosas.
**Docente:** Jhorman Andrés Villanueva Vivas.

## Alcance de esta prueba

Se inició en Docker Desktop una pila de cuatro servicios: Mosquitto, colector Python, InfluxDB OSS 2 y Grafana. Las lecturas se generaron con **un cliente MQTT de prueba en el computador**, con valores simulados de 31,2 °C y 32,5 °C y humedad relativa de 64,5 %. **Esta prueba no demuestra que el ESP32 de Wokwi haya enviado datos al broker propio ni que la pila esté instalada en AWS.** El proyecto público de Wokwi de la Práctica 1 usa otra conexión y permanece separado.

## Resultados observados

1. `docker compose ps` mostró los cuatro servicios en estado `Up`. Tras la revisión final, los tres puertos del computador quedaron limitados a `127.0.0.1`: Mosquitto 1883, InfluxDB 8086 y Grafana 3000.
2. El cliente de prueba publicó dos mensajes autenticados en `invernadero1/telemetria` con identificador de arranque `PRACTICA2CHECK` y secuencias 1 y 2. El broker confirmó la publicación con QoS 1.
3. El colector registró las lecturas en `readings.csv` y en su cola local SQLite, y confirmó su escritura en InfluxDB. La consulta de InfluxDB devolvió la temperatura y humedad esperadas, con las etiquetas de arranque y secuencia.
4. La API de Grafana informó estado `ok`, reconoció la fuente `Savia InfluxDB` y el tablero `Savia IoT | Invernadero de tomates`. Una consulta del panel devolvió puntos de la serie de temperatura.
5. Grafana cargó la regla `savia-temp-alta`, el contacto MQTT `Savia MQTT` y la política de notificación. Tras superar 30 °C, la regla figuró como `firing` y `health ok`. Un suscriptor autenticado **recibió un mensaje de alerta** en `invernadero1/alertas`. Esto comprueba la notificación local, no una entrega por correo ni a un teléfono.
6. Las pruebas unitarias del colector pasaron: validación de lecturas y deduplicación/reintento de la cola. No se guardaron contraseñas ni tokens en el repositorio.

## Pendiente para acreditar la práctica completa

- Instalar o verificar esta pila en el laboratorio AWS Academy, en la VM Ubuntu adecuada y con capacidad suficiente. Restringir el acceso a InfluxDB y Grafana; habilitar MQTT solo para la demostración, con credenciales temporales.
- Crear una copia **privada** de la simulación de la Práctica 2, configurar la IP y clave temporal allí, variar el DHT22 y comprobar que las nuevas lecturas lleguen a MQTT, CSV, InfluxDB y Grafana. No publicar la clave dentro de un Wokwi compartido.
- Guardar capturas legibles de AWS, Wokwi, tópicos, serie temporal, tablero y alerta recibida; presentar el recorrido al grupo.
- Aclarar con el docente el numeral de la subred de base de datos: el enunciado de esta actividad menciona una subred pública, mientras que la Práctica 1 usó PostgreSQL privado. Esta prueba local no acredita una topología de subred AWS.

**Reconocimiento de AWS:** en el Learner Lab se encontró la instancia existente `i-01f3188a0db02ef65`, tipo `t3.micro`, con 1 GiB de RAM y volumen raíz de 12 GiB. El grupo de seguridad permitía HTTP 80 desde Internet y SSH 22 solo desde `127.0.0.1/32`; no tenía el puerto MQTT abierto. Estos datos no prueban que la pila de esta práctica esté allí instalada. Antes de desplegar, hay que resolver capacidad, acceso y exposición temporal del broker sin afectar la Práctica 1 ni superar el límite de gasto acordado.

**Estado de entrega académica:** preparar los archivos y compartir el repositorio no equivale a subir la actividad en CampusDigital. El 24 de octubre se observó allí el cierre para el 31 de octubre de 2026 a las 12:00, hora de Colombia.
