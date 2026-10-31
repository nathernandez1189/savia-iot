# Evidencias de la Práctica 2

Estas comprobaciones corresponden al **24 de octubre de 2026**. Se conservan sus resultados y límites; el traslado a esta carpeta solo ajusta los enlaces necesarios.

| Evidencia | Qué acredita | Límite |
| --- | --- | --- |
| [Prueba local](EVIDENCIA_LOCAL_2026-10-24.md) | Mosquitto, colector, CSV, InfluxDB, Grafana y recepción de una alerta en Docker local | Los mensajes se generaron con un cliente de prueba en el computador. |
| [Prueba AWS](EVIDENCIA_AWS_2026-10-24.md) | Lecturas del ESP32 simulado en Wokwi, persistencia, base en segunda EC2, Grafana y notificaciones MQTT | Las pruebas sintéticas se identifican por separado; la alerta automática se provocó con un dato sintético. |
| [Captura de Grafana en AWS](grafana-aws-2026-10-24.png) | Cuatro paneles con series y últimos valores | Mezcla lecturas de Wokwi y del cliente de prueba. El último valor visible es sintético. |

Una captura o una sesión histórica no garantizan disponibilidad actual de AWS. Para acreditar una ejecución nueva, seguir el [checklist](../checklist-entrega.md), comparar `boot` y `seq` y guardar otra evidencia fechada, sin sustituir estas.

[Volver a la guía](../README.md) · [Descargar la presentación](../entregables.md)
