# Guion de exposición · Savia IoT en AWS

**Duración sugerida:** 5 a 7 minutos. **Materia:** Inteligencia Artificial Aplicada a Internet de las Cosas.  
**Integrantes:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés.

## 1. Problema y objetivo (Natalia)

«Planteamos un invernadero de tomates donde importa conocer la temperatura y la humedad del aire y responder a cambios de temperatura. Construimos una simulación IoT que permite monitorear esas variables, accionar una ventilación representada por un LED y conservar las lecturas en una aplicación web. El prototipo es académico: no afirmamos haber medido un cultivo real».

Mostrar [Wokwi](https://wokwi.com/projects/477744536654042113) y señalar ESP32, DHT22 y LED.

## 2. Sensores y decisión local (Sidney)

«El DHT22 entrega temperatura y humedad relativa del aire. El ESP32 lee ambos valores. En modo automático enciende el indicador de ventilación si la temperatura supera 30 °C y lo apaga al bajar de 27 °C. Ese intervalo evita que cambie de estado constantemente cerca de un solo umbral. Si la conexión se pierde, la regla local sigue funcionando».

En Wokwi variar el DHT22; mostrar monitor serial y LED. Si la simulación no compila o el broker no responde durante la clase, explicar la lógica con el código y mostrar la evidencia guardada, sin declarar una prueba en vivo que no ocurrió.

## 3. Envío y almacenamiento (José)

«El ESP32 publica telemetría por MQTT. Un puente instalado en la máquina Ubuntu de AWS recibe esos mensajes y los entrega a nuestra aplicación Python. La aplicación valida, descarta duplicados y guarda cada lectura en PostgreSQL y en un archivo CSV. El token del servidor permanece en AWS y no aparece en el proyecto público Wokwi».

Mostrar `/health`, `/api/readings?limit=10` y `/api/readings.csv` desde una conexión que permita HTTP; comparar `boot` y `seq` de una fila. No mostrar secretos ni consola de variables de entorno. En la última verificación se observaron 13 lecturas y las secuencias 23–25 de un mismo arranque.

## 4. Infraestructura y resultados (David)

«Usamos AWS Academy Learner Lab. CloudFormation creó una VPC, una subred pública para el servidor Ubuntu, dos subredes privadas para PostgreSQL, una IP elástica y grupos de seguridad. RDS no está expuesto a internet; solo el servidor web puede conectarse a su puerto. El flujo completo de la simulación llegó a base de datos y CSV».

Mostrar la pila `savia-iot-lab` y sus recursos, sin abrir pestañas de credenciales. La pila estaba en `CREATE_COMPLETE` con 16 recursos el 24 de octubre. La eliminación está programada para el 1 de noviembre a las 23:00, hora de Bogotá, y debe verificarse posteriormente.

## Cierre en equipo

«Se cumplió la demostración en AWS con datos simulados y almacenamiento dual. Aún no hemos documentado una ejecución local separada en Ubuntu; las pruebas automatizadas se ejecutaron en macOS y pasaron, pero no sustituyen ese requisito. El MQTT público tampoco autentica el origen de los mensajes, por lo que no usaríamos esta configuración para un invernadero real. Como siguiente paso probaríamos un sensor y actuador físicos, un canal autenticado y una instalación local Ubuntu documentada».

**Enlaces:** [Repositorio](https://github.com/nathernandez1189/savia-iot) · [Wokwi](https://wokwi.com/projects/477744536654042113) · [Evidencia AWS](Evidencia_AWS_2026-10-24.md).  
**Nota de acceso:** Chrome del equipo bloqueó HTTP hacia la VM aunque AWS CloudShell sí obtuvo respuesta. No anunciar un enlace HTTPS de AWS: aún no existe certificado.
