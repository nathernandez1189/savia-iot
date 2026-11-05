# Evidencias de la Práctica 3

La [verificación AWS del 3 de noviembre de 2026](EVIDENCIA_AWS_SERVERLESS_2026-11-03.md) registra recursos de AWS IoT Core, DynamoDB, Lambda, API Gateway y S3, una publicación MQTT con certificado X.509, el aumento de seis a siete registros en DynamoDB, una respuesta de consulta y la publicación de un comando desde la API.

| Evidencia | Qué acredita | Qué no acredita por sí sola |
| --- | --- | --- |
| [Despliegue y prueba AWS](EVIDENCIA_AWS_SERVERLESS_2026-11-03.md) | La ruta de una publicación MQTT de prueba hacia DynamoDB y respuestas de la API y el sitio en esa sesión. | Origen físico inequívoco del ESP32, continuidad de conexión, ejecución de la orden en el actuador o una descarga CSV revisada. |
| [Código del dispositivo](../esp32/esp32_serverless/esp32_serverless.ino) | Que existen lectura del DHT22, publicación, suscripción a órdenes y control local en el firmware. | Que el firmware esté cargado en un dispositivo y conectado hoy. |
| [Dashboard y backend](../s3-dashboard/index.html) | Que la interfaz implementa consulta, botones y descarga CSV. | Una prueba funcional actual del sitio, el CSV o el actuador. |

La tabla DynamoDB puede contener datos semilla creados durante el despliegue. Para una nueva comprobación, seguir una lectura identificada por dispositivo, hora y valor desde el ESP32 hasta el sitio y el CSV. Guardar los resultados con una fecha nueva sin reemplazar este registro histórico. Nunca subir certificados privados, contraseñas ni capturas que los expongan.

[Volver a la guía](../README.md) · [Checklist de entrega](../checklist-entrega.md)
