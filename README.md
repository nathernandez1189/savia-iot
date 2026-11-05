# Savia IoT · Invernadero de tomates

[![Pruebas](https://github.com/nathernandez1189/savia-iot/actions/workflows/pruebas.yml/badge.svg)](https://github.com/nathernandez1189/savia-iot/actions/workflows/pruebas.yml)
[![Publicar tablero](https://github.com/nathernandez1189/savia-iot/actions/workflows/pages.yml/badge.svg)](https://github.com/nathernandez1189/savia-iot/actions/workflows/pages.yml)

Prototipo académico para un invernadero de tomates (*Solanum lycopersicum*): las Prácticas 1 y 2 documentan lecturas simuladas con ESP32 y DHT22; la Práctica 3 añade código para ESP32, AWS IoT Core, DynamoDB y un tablero en S3. Los cálculos agronómicos son reglas y estimaciones de demostración, no un modelo entrenado o validado. Asignatura **Inteligencia Artificial Aplicada a Internet de las Cosas**, UAO, 2026-2.

**Equipo:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés.  
**Docente:** Jhorman Andrés Villanueva Vivas.

[Abrir tablero](https://nathernandez1189.github.io/savia-iot/) · [Wokwi del tablero público](https://wokwi.com/projects/479406694310787073) · [Estado y siguientes pasos](00-indice.md)

| Parte | Qué contiene | Guía |
| --- | --- | --- |
| Práctica 1 | ESP32 → MQTT público → puente HTTP → API Python → PostgreSQL/SQLite y CSV | [practica-1/](practica-1/README.md) |
| Práctica 2 | ESP32 → Mosquitto autenticado → colector → InfluxDB/CSV → Grafana | [practica2/](practica2/README.md) |
| Práctica 3 | ESP32 (mTLS X.509) → AWS IoT Core → IoT Rule → DynamoDB → Lambda IA → API Gateway → S3 | [practica-3/](practica-3/README.md) |
| Tablero web | React + Vite, telemetría MQTT, historial local y clima exterior | [dashboard/](dashboard/README.md) |
| Proyecto final | Espacio para definir y evaluar la futura parte de IA | [proyecto-final/](proyecto-final/README.md) |

## Cómo empezar

1. Abre el [tablero](https://nathernandez1189.github.io/savia-iot/) y pulsa **Abrir Wokwi**. Inicia la simulación para producir lecturas nuevas. La conexión depende del simulador y de un broker público de pruebas.
2. Para reproducir el servidor local o el almacenamiento en AWS, sigue la [guía de la Práctica 1](practica-1/README.md). Para Mosquitto propio, InfluxDB y Grafana, sigue la [Práctica 2](practica2/README.md). Para AWS IoT Core, DynamoDB y el tablero S3, sigue la [guía de la Práctica 3](practica-3/README.md) y su checklist de verificación.
3. Para modificar la página pública, trabaja en [dashboard/](dashboard/README.md). GitHub Actions ejecuta las pruebas y publica desde ese código cuando se integra un cambio en `main`.

## Evidencias y entregables

- Práctica 1: [AWS](practica-1/evidencias/Evidencia_AWS_2026-10-24.md), [Ubuntu local](practica-1/evidencias/Evidencia_Ubuntu_Local_2026-10-24.md), [checklist](practica-1/checklist-entrega.md) e [informe y presentación descargables](practica-1/entregables.md).
- Práctica 2: [AWS](practica2/evidencias/EVIDENCIA_AWS_2026-10-24.md), [prueba local](practica2/evidencias/EVIDENCIA_LOCAL_2026-10-24.md), [checklist](practica2/checklist-entrega.md) y [presentación descargable](practica2/entregables.md).
- Práctica 3: [guía técnica](practica-3/README.md), [checklist](practica-3/checklist-entrega.md), [evidencias](practica-3/evidencias/README.md) y [entregables](practica-3/entregables.md). La prueba fechada de MQTT y DynamoDB no acredita por sí sola el origen físico del ESP32 ni la ejecución de un comando en el actuador.
- Contexto de mantenimiento: [AGENTS.md](AGENTS.md) y [decisiones.md](decisiones.md).
