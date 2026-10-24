# Savia IoT | Invernadero de tomates

Proyecto académico de **Inteligencia Artificial Aplicada a Internet de las Cosas**. Simulamos un ESP32 con sensor DHT22 para registrar la temperatura y la humedad relativa del **aire** en un invernadero de tomates. El ESP32 aplica una regla local de ventilación; un LED representa el actuador.

**Equipo:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés.  
**Docente:** Jhorman Andrés Villanueva Vivas.

[Simulación en Wokwi](https://wokwi.com/projects/477744536654042113) · [Tablero Savia IoT](https://nathernandez1189.github.io/savia-iot/) · [Implementación y evidencia](CHECKLIST_ENTREGA_PRACTICA_1.md)

## Relación con la Práctica 1

El enunciado solicita un caso de monitoreo, un servidor Ubuntu, envío de lecturas desde el ESP32, almacenamiento en CSV y base de datos, una implementación posterior en AWS, repositorio y exposición. Este repositorio reúne el prototipo, el servidor, la plantilla AWS y resultados fechados. Se comprobaron **Ubuntu local en Docker** y, por separado, la **VM Ubuntu en AWS**. La [guía](GUIA_PRACTICA_1.md) explica cómo repetir ambas etapas.

## Qué contiene el repositorio

- [wokwi/](wokwi/): circuito, programa ESP32 y bibliotecas de la simulación.
- [server/](server/): aplicación Python, puente MQTT, servicios de ejecución y prueba del servidor.
- [local-ubuntu/Dockerfile](local-ubuntu/Dockerfile): entorno Ubuntu 24.04 para reproducir la etapa local con SQLite y CSV.
- [aws/savia-iot.yaml](aws/savia-iot.yaml): plantilla CloudFormation para AWS Academy Learner Lab. Define una VM Ubuntu en subred pública, IP elástica y PostgreSQL RDS en subredes privadas.
- [GUIA_PRACTICA_1.md](GUIA_PRACTICA_1.md): arquitectura, reproducción y comprobaciones.
- [CHECKLIST_ENTREGA_PRACTICA_1.md](CHECKLIST_ENTREGA_PRACTICA_1.md): informe breve de implementación y evidencia por componente.
- [entregables/Evidencia_AWS_2026-10-24.md](entregables/Evidencia_AWS_2026-10-24.md): resultados observados el 24 de octubre de 2026 y sus límites.
- [entregables/Evidencia_Ubuntu_Local_2026-10-24.md](entregables/Evidencia_Ubuntu_Local_2026-10-24.md): prueba local de Wokwi a SQLite y CSV.
- [entregables/Savia_IoT_Practica_1_AWS.pptx](entregables/Savia_IoT_Practica_1_AWS.pptx): presentación de ocho diapositivas para explicar el caso, la arquitectura, la simulación, las pruebas y sus límites.
- [entregables/Savia_IoT_Practica_1_Entrega_2026-10-24.pdf](entregables/Savia_IoT_Practica_1_Entrega_2026-10-24.pdf): informe formal de tres páginas con los enlaces y resultados de ambas etapas.
- [index.html](index.html), [assets/](assets/) y [brand/](brand/): versión compilada del tablero publicada en GitHub Pages. El código fuente editable del tablero **no forma parte de este repositorio**.

## Funcionamiento

El DHT22 simulado entrega temperatura y humedad relativa del aire. El ESP32 publica las lecturas por MQTT; un puente en Ubuntu las recibe y las entrega por HTTP a la aplicación Python. Esta valida cada registro y lo conserva en PostgreSQL y CSV. En modo automático, el indicador de ventilación se enciende por encima de 30 °C y se apaga por debajo de 27 °C; entre esos límites mantiene su estado. La decisión local funciona aunque la conexión se interrumpa.

El tablero muestra las lecturas del prototipo y permite consultar historial y controles. Su sección de clima utiliza Open-Meteo para **estimaciones exteriores y pronósticos** de la ubicación que el usuario seleccione. Estos datos no son mediciones dentro del invernadero y nunca reemplazan una lectura ausente del DHT22. No se ha entrenado un modelo de inteligencia artificial ni se han medido plantas reales.

## Evidencia y límites

El **24 de octubre de 2026** se verificó en AWS el servidor Ubuntu, PostgreSQL privado, la API y el CSV. Durante una sesión de Wokwi, el registro aumentó de 4 a 13 lecturas. La pasarela Wi-Fi falló temporalmente en otra comprobación; tras reiniciar Wokwi, el contador de AWS pasó de **13 a 23** y las secuencias 23 y 24 del mismo arranque aparecieron en la API y CSV. El Ubuntu local recibió las secuencias 22–25 de ese arranque y las guardó en SQLite y CSV. Los detalles y límites constan en las [evidencias AWS](entregables/Evidencia_AWS_2026-10-24.md) y [local](entregables/Evidencia_Ubuntu_Local_2026-10-24.md). La demostración se debe repetir antes de la exposición porque la conexión depende de servicios de prueba.

La comunicación utiliza un broker MQTT público de pruebas y solo datos simulados. La instalación AWS ofrece HTTP, sin HTTPS. La dirección de la VM es temporal y depende de que el laboratorio siga activo; GitHub Pages es un tablero separado del servidor de almacenamiento.
