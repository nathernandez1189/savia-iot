# Práctica 2: verificación en AWS Academy — 24 de octubre de 2026

**Proyecto:** Savia IoT, monitoreo y ventilación simulada de un invernadero de tomates.  
**Asignatura:** Inteligencia Artificial Aplicada a Internet de las Cosas.  
**Docente:** Jhorman Andrés Villanueva Vivas.  
**Equipo:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés.

## Infraestructura observada

Se reutilizó la instancia Ubuntu de AWS Academy Learner Lab de la Práctica 1 (`i-01f3188a0db02ef65`), ampliada a `t3.small` dentro del límite de gasto autorizado. La aplicación anterior continuó respondiendo `HTTP 200` en `/health`. En `/opt/savia-iot-practica2` se instalaron Docker y Compose y se levantaron **Mosquitto, colector, InfluxDB OSS 2 y Grafana**; los cuatro aparecieron activos. InfluxDB y Grafana respondieron `HTTP 200` en sus comprobaciones locales y sus puertos están limitados a `127.0.0.1` del host. El puerto MQTT 1883 se abrió temporalmente para la demostración; el broker exige usuario y contraseña y aplica listas de acceso por tópico. La base PostgreSQL de la Práctica 1 sigue siendo un recurso distinto y privado.

## Recorrido de una lectura de prueba

La prueba reproducible está en [`smoke_test.sh`](smoke_test.sh). Publicó desde la propia VM, mediante un **cliente MQTT de prueba autenticado**, un mensaje identificado como `AWSCHECK1792859337`: temperatura **31,2 °C**, humedad **64,5 %** y ventilación encendida. El registro apareció en `readings.csv` y en la cola SQLite. El colector confirmó posteriormente `sent=1`; una consulta de InfluxDB devolvió puntos del mismo identificador con la etiqueta `origen=simulacion`. La primera consulta se hizo mientras la lectura seguía en la cola (`sent=0`), por lo que se repitió y se corrigió el script para esperar confirmación antes de declarar éxito. La ejecución definitiva terminó con código 0.

Grafana respondió por su API y mostró una alerta de temperatura superior a 30 °C en estado **active**, con receptor **Savia MQTT**. El tablero y la notificación por el tópico `invernadero1/alertas` ya se habían verificado en la [prueba local](EVIDENCIA_LOCAL_2026-10-24.md). En AWS se verificó la regla activa y su receptor configurado; **no se capturó una nueva notificación recibida en AWS** durante esta comprobación.

## Alcance y pasos restantes

La lectura anterior es **sintética**: no demuestra un envío desde Wokwi. La [simulación pública de la Práctica 2](https://wokwi.com/projects/478779944323491841) conserva el código sin contraseñas. Compiló y arrancó, pero la pasarela Wi-Fi de Wokwi presentó errores en el intento de conexión. Además, publicar la clave en ese proyecto expondría el broker. Para afirmar que el ESP32 alimenta el tablero de AWS falta una prueba con credencial temporal privada, confirmación de una secuencia única en MQTT, CSV e InfluxDB, captura del dashboard y rotación posterior de la clave. También falta la sustentación y el envío formal al campus por el equipo.

El numeral de subred de la base de datos en el enunciado se debe revisar con el docente antes de declarar cumplimiento: aquí InfluxDB corre en la misma VM pública con el puerto cerrado al exterior; no se creó una base administrada adicional ni se afirmó que exista una subred pública independiente para ella. El acceso MQTT abierto y la VM ampliada deben retirarse o reducirse tras la demostración prevista hasta el **1 de noviembre de 2026**, según el límite de gasto del equipo.
