# Savia IoT: arquitectura serverless para el monitoreo de un invernadero de tomates

**Informe de la Práctica 3**  
**Asignatura:** Inteligencia Artificial Aplicada a Internet de las Cosas  
**Docente:** Jhorman Andrés Villanueva Vivas  
**Integrantes:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés  
**Universidad Autónoma de Occidente — Especialización en Inteligencia Artificial**  
**Fecha del informe:** noviembre de 2026

## Resumen

Savia IoT propone una arquitectura administrada en AWS para recibir lecturas de temperatura y humedad de un ESP32 con DHT22, conservarlas en DynamoDB y presentarlas en un tablero web alojado en Amazon S3. El repositorio publica el firmware, la función Lambda, el tablero y el programa de despliegue. La [evidencia del 3 de noviembre de 2026](evidencias/EVIDENCIA_AWS_SERVERLESS_2026-11-03.md) registra servicios creados y una publicación MQTT con certificado X.509 que elevó de seis a siete los registros de DynamoDB. También documenta una respuesta de consulta y la publicación de un comando remoto desde la API. La prueba no identifica inequívocamente al ESP32 físico como origen de ese mensaje ni muestra la ejecución del comando en el actuador; este informe separa esas funciones implementadas de los resultados comprobados.

**Palabras clave:** Internet de las cosas, ESP32, AWS IoT Core, MQTT, DynamoDB, Lambda, S3.

## Introducción y objetivo

El caso de uso representa el monitoreo del aire en un invernadero de tomates. Un sensor DHT22 conectado a un ESP32 proporciona temperatura y humedad relativa. La práctica busca transmitir esas lecturas a AWS IoT Core mediante MQTT, almacenarlas para su consulta posterior y mostrarlas en un dashboard con exportación CSV y control remoto de un actuador. Esta etapa sustituye el bróker autogestionado de la Práctica 2 por servicios de AWS y conserva el propósito de explicar todo el recorrido del dato.

## Arquitectura e implementación

El [firmware](esp32/esp32_serverless/esp32_serverless.ino) contempla MQTT sobre TLS con certificados X.509, publicación en `invernadero1/telemetria` y suscripción a `invernadero1/actuador`. Una regla de AWS IoT Core dirige las publicaciones a la tabla `telemetria_invernadero` de DynamoDB. [AWS Lambda](lambda/lambda_function.py), detrás de API Gateway, consulta los registros, genera una respuesta CSV y publica órdenes de control. El [dashboard](s3-dashboard/index.html) se aloja como sitio estático en S3 y utiliza esas rutas. La [guía](README.md) y el [programa de despliegue](infra/deploy_serverless.py) permiten examinar la configuración; las credenciales privadas no forman parte del código público.

El sistema calcula indicadores como déficit de presión de vapor y proyecciones de corto plazo a partir de temperatura y humedad. Estos resultados son estimaciones basadas en fórmulas y reglas del prototipo. Los porcentajes de riesgo no deben interpretarse como probabilidades validadas para tomar decisiones agronómicas, y el repositorio no acredita un modelo de aprendizaje automático entrenado con datos de cultivo.

## Resultados documentados

La evidencia fechada informa que AWS IoT Core, la regla de enrutamiento, DynamoDB, Lambda y API Gateway estaban activos en la sesión, y que el sitio de S3 respondió HTTP 200. Una publicación MQTT con certificado devolvió código 0 y el número de registros de DynamoDB pasó de seis a siete. La ruta de consulta devolvió un diagnóstico para una muestra de 31,2 °C. La ruta de control respondió HTTP 200 con `published_mqtt: true`. En conjunto, estas observaciones respaldan la recepción y persistencia de un mensaje de prueba y la emisión de una orden desde la API durante esa sesión.

## Alcance de la evidencia

La publicación MQTT no permite atribuir la lectura al ESP32 físico sin comparar un identificador y una hora con su monitor serial. Asimismo, la respuesta de publicación de la API no demuestra recepción ni ejecución de la orden en el dispositivo. El código incluye un botón de CSV y controles en la interfaz, pero la evidencia publicada no contiene una descarga revisada ni una secuencia que muestre el cambio del actuador. Los registros iniciales de DynamoDB incluyen datos semilla; no se presentan como lecturas del sensor. El estado actual del laboratorio AWS debe comprobarse nuevamente antes de una demostración.

## Conclusiones

La Práctica 3 reúne los componentes de software solicitados para una arquitectura de IoT con servicios administrados de AWS. La prueba fechada confirma una publicación MQTT almacenada en DynamoDB y respuestas de las rutas de consulta y control. Para completar la verificación funcional, el equipo debe seguir una misma lectura identificada desde el ESP32 hasta DynamoDB, el sitio S3 y el CSV, y observar en el dispositivo el efecto de una orden remota. La presentación frente a los compañeros y el envío por el canal del curso se acreditan por separado.

## Acceso y referencia

- [Repositorio general Savia IoT](https://github.com/nathernandez1189/savia-iot).
- [Carpeta de la Práctica 3](https://github.com/nathernandez1189/savia-iot/tree/main/practica-3).
- [Checklist y plan de comprobación](checklist-entrega.md).
- Villanueva Vivas, J. A. (2026). *Práctica 3: Arquitectura Serverless para IoT* [Enunciado de clase]. Especialización en Inteligencia Artificial, Universidad Autónoma de Occidente.
