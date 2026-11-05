# Práctica 3 | Implementación y checklist de entrega

**Asignatura:** Inteligencia Artificial Aplicada a Internet de las Cosas  
**Docente:** Jhorman Andrés Villanueva Vivas  
**Equipo:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés  
**Evidencia técnica de referencia:** 3 de noviembre de 2026

[Guía](README.md) · [Evidencias](evidencias/README.md) · [Entregables](entregables.md)

## Correspondencia con el enunciado

| Requisito | Implementación publicada | Evidencia disponible y alcance |
| --- | --- | --- |
| Caso de temperatura y humedad | Invernadero de tomates, ESP32 y DHT22 | Caso definido en [README](README.md) y [firmware](esp32/esp32_serverless/esp32_serverless.ino). |
| AWS IoT Core y MQTT | Thing, política, certificado X.509 y regla IoT | [Prueba del 3 de noviembre](evidencias/EVIDENCIA_AWS_SERVERLESS_2026-11-03.md): publicación MQTT con certificado y código 0. No identifica de forma inequívoca al ESP32 físico como origen. |
| Base de datos | IoT Rule hacia DynamoDB | El conteo registrado pasó de 6 a 7 tras la publicación de prueba. La tabla contiene además datos semilla; no confundirlos con lecturas del dispositivo. |
| Dashboard, actuador y CSV | [Sitio S3](s3-dashboard/index.html), [Lambda](lambda/lambda_function.py) y API Gateway | Se registró HTTP 200 del sitio y publicación de orden desde la API. No consta una descarga CSV examinada ni el cambio de salida observado en el ESP32. |
| Alojamiento S3 | Configuración en [despliegue](infra/deploy_serverless.py) | El sitio respondió HTTP 200 el 3 de noviembre. Esta prueba histórica no garantiza disponibilidad actual. |
| Código, README y paso a paso | Esta carpeta contiene firmware, infraestructura, backend, tablero, guía y diagrama | Publicado en [GitHub](https://github.com/nathernandez1189/savia-iot/tree/main/practica-3). |
| Presentación frente al grupo | Material técnico disponible para preparar la sustentación | La realización de la exposición se confirma en clase, no por el repositorio. |

La verificación de la API y del sitio no sustituye la prueba del sensor, de la descarga ni del actuador. Los indicadores de riesgo calculados por el código no son probabilidades validadas ni un modelo entrenado.

## Antes de una nueva demostración

- [ ] Confirmar el acceso al laboratorio AWS Academy y el estado **actual** de IoT Core, DynamoDB, Lambda, API Gateway y S3.
- [ ] Revisar permisos y alcance de los certificados; no mostrar secretos ni claves privadas al compartir pantalla.
- [ ] Abrir el sitio S3 vigente y comprobar que consulta su API, no el tablero de GitHub Pages.
- [ ] Preparar un identificador o marca de tiempo para seguir una lectura nueva del dispositivo de extremo a extremo.

## Recorrido que se muestra al profesor

| Paso | Qué mostrar | Cuándo queda acreditado |
| --- | --- | --- |
| 1. Dispositivo | ESP32, DHT22 y monitor serial | Aparece una lectura nueva y conexión AWS IoT Core. Identificar origen y hora. |
| 2. Comunicación | Cliente de prueba MQTT de AWS IoT Core | Aparece el mismo mensaje en `invernadero1/telemetria`; distinguirlo de una publicación sintética desde otro cliente. |
| 3. Persistencia | DynamoDB | El mismo dispositivo, hora y valores están en un registro nuevo. No usar datos semilla como evidencia de sensor. |
| 4. Dashboard | Sitio S3 y respuesta de `/sensor` | Se ven los valores correspondientes y su hora. |
| 5. Exportación | Botón CSV y archivo descargado | El archivo contiene la lectura identificada. |
| 6. Control remoto | Botones Encender, Apagar y Automático; serial y salida del ESP32 | El ESP32 recibe cada orden y el actuador cambia según el modo. Una respuesta `published_mqtt: true` no basta. |

## Evidencias para conservar

- [ ] Captura del ESP32 y lectura nueva, sin credenciales visibles.
- [ ] Mensaje MQTT y registro DynamoDB de la misma lectura.
- [ ] Sitio S3 con la misma lectura, fecha y hora.
- [ ] CSV descargado con esa lectura.
- [ ] Comando publicado, comando recibido y cambio del actuador.
- [ ] Fecha, entorno, identificadores y límites de la nueva prueba en [evidencias/](evidencias/README.md).
- [ ] Confirmar la sustentación y el envío oficial en el curso; GitHub no equivale a entrega formal.

La [evidencia del 3 de noviembre](evidencias/EVIDENCIA_AWS_SERVERLESS_2026-11-03.md) se conserva como resultado histórico y no debe marcar automáticamente las casillas de una demostración posterior.
