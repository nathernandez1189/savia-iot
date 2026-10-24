# Evidencia de la Práctica 1 | Ubuntu local

**Fecha:** 24 de octubre de 2026

**Entorno:** Ubuntu 24.04 en un contenedor Docker ejecutado en el computador del equipo; separado de la VM de AWS.

**Fuente de los datos:** ESP32 y DHT22 simulados en [Wokwi](https://wokwi.com/projects/477744536654042113).

La aplicación Python se construyó con [local-ubuntu/Dockerfile](../local-ubuntu/Dockerfile) y se ejecutó en el puerto local `127.0.0.1:18000`. El almacenamiento de esta etapa fue SQLite y CSV en un volumen local. La misma imagen superó las dos pruebas del repositorio: validación/autorización/deduplicación/almacenamiento y aceptación de mensajes MQTT.

Primero se envió una **muestra manual de verificación** (`UBUNTU24TEST`, secuencia 1). La API respondió `201`, la ruta de salud indicó `database: sqlite, readings: 1`, y la fila apareció en SQLite y CSV. Esta muestra comprueba el servidor; no se atribuye al ESP32.

Después se inició el puente MQTT dentro del mismo Ubuntu local. Wokwi mostró `WiFi: Connected to Wokwi-GUEST` y `MQTT conectado: dashboard habilitado`. El puente registró las secuencias **22, 23, 24 y 25** del arranque `8b9a8e13`, cada una con **26,0 °C y 65,0 %**. La ruta de salud pasó a **5 registros**: cuatro del simulador y uno manual. Las cuatro secuencias del ESP32 se comprobaron tanto en la tabla SQLite como en `readings.csv`.

| Secuencia Wokwi | SQLite local | CSV local |
|---|---|---|
| `8b9a8e13/22` | 26,0 °C; 65,0 % | Coincide |
| `8b9a8e13/23` | 26,0 °C; 65,0 % | Coincide |
| `8b9a8e13/24` | 26,0 °C; 65,0 % | Coincide |
| `8b9a8e13/25` | 26,0 °C; 65,0 % | Coincide |

El simulador había mostrado antes una falla de su pasarela Wi-Fi; al reiniciarlo se recuperó la conexión y se obtuvieron estos resultados. Esta evidencia prueba la sesión fechada, no disponibilidad permanente. El DHT22 y el actuador son simulados, y el broker MQTT es público. La contraseña de prueba local no forma parte del código del ESP32 ni del repositorio.

[Procedimiento para repetir la prueba](../GUIA_PRACTICA_1.md) · [Evidencia de AWS](Evidencia_AWS_2026-10-24.md)
