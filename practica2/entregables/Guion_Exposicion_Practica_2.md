# Guion breve de sustentación · Savia IoT, Práctica 2

**Asignatura:** Inteligencia Artificial Aplicada a Internet de las Cosas
**Docente:** Jhorman Andrés Villanueva Vivas
**Equipo:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés.

Usar junto con la [presentación](Savia_IoT_Practica_2_Presentacion.pptx). Cada integrante puede hablar aproximadamente un minuto y dejar dos minutos para mostrar el tablero.

1. **Natalia, problema y objetivo.** «Elegimos un invernadero de tomates. Queremos observar temperatura y humedad del aire para detectar cambios y conservar un historial. Por ahora trabajamos con un DHT22 simulado; no estamos mostrando mediciones de un cultivo físico».
2. **Sidney, dispositivo y comunicación.** «En Wokwi, el ESP32 lee el sensor y publica por MQTT con usuario y clave. Separamos los temas de temperatura, humedad y telemetría. La ventilación sigue funcionando localmente aunque se interrumpa la conexión».
3. **José, infraestructura y datos.** «La primera VM Ubuntu en AWS recibe los mensajes mediante Mosquitto. El colector los guarda en CSV y en InfluxDB. Ubicamos InfluxDB en otra VM y otra subred pública; el puerto de la base solo admite conexiones desde el servidor principal. El proyecto y la arquitectura están en GitHub».
4. **Jarvin, visualización y prueba.** «Grafana muestra las series y los valores recientes. Siete lecturas del ESP32 simulado llegaron al CSV y produjeron catorce puntos de temperatura y humedad en InfluxDB. También provocamos una lectura sintética de 31,2 °C: la regla generó una alerta y un cliente MQTT recibió la notificación en AWS. Distinguimos esa prueba sintética de las lecturas de Wokwi».

## Demostración sugerida

Abrir la [captura del tablero en AWS](../evidencias/grafana-aws-2026-10-24.png) y señalar las gráficas, las etiquetas de origen y la última lectura. Abrir la [evidencia técnica](../EVIDENCIA_AWS_2026-10-24.md) para mostrar el identificador `39c72c8e` de Wokwi y `AWSCHECK1792862155` de la prueba de alerta. Si se desea repetir la simulación en vivo, configurar una **credencial temporal nueva** en una copia privada de Wokwi; el enlace público no contiene una clave funcional. Retirarla y rotarla después. Evitar mostrar `.env`, contraseñas o tokens en pantalla.

**Al cerrar:** el sistema demostró recepción, almacenamiento, visualización y alerta con datos simulados. La disponibilidad permanente y las mediciones físicas quedan fuera de esta prueba académica. La exposición y el envío por CampusDigital deben realizarse efectivamente por el equipo.
