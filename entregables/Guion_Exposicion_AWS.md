# Esquema de exposición | Savia IoT

**Asignatura:** Inteligencia Artificial Aplicada a Internet de las Cosas  
**Docente:** Jhorman Andrés Villanueva Vivas  
**Integrantes:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés.

Este esquema sirve para preparar la presentación; el equipo puede repartir las intervenciones. **No es constancia de que la exposición ya se haya realizado.**

## 1. Problema y prototipo

Presentar el caso de un invernadero de tomates en el que interesa conocer la temperatura y la humedad relativa del aire. Abrir el [circuito en Wokwi](https://wokwi.com/projects/477744536654042113) e identificar ESP32, DHT22 y LED. Aclarar que todo es simulado y que el LED representa la ventilación.

## 2. Lectura y decisión local

Variar la temperatura del DHT22 y observar el monitor serial. En modo AUTO, la ventilación se activa cuando supera 30 °C y se desactiva cuando baja de 27 °C; entre los dos umbrales conserva el estado. Explicar que esa regla continúa aunque falle la comunicación. Esta lógica es automatización por umbrales, **no** un modelo de IA entrenado.

## 3. Envío y almacenamiento

Describir el recorrido real: ESP32 → MQTT → puente en Ubuntu → aplicación Python → PostgreSQL y CSV. Mostrar una lectura con el mismo identificador de arranque y secuencia en la API y el CSV; si es posible, mostrar también la fila en PostgreSQL sin revelar credenciales. El ESP32 no envía HTTP directamente en la configuración activa.

## 4. Despliegue y límites

En AWS CloudFormation señalar la VM Ubuntu de la subred pública, la IP elástica, las subredes privadas de RDS y los grupos de seguridad. La base no tiene acceso público. La [evidencia del 24 de octubre](Evidencia_AWS_2026-10-24.md) registró 13 lecturas, pero en una prueba posterior falló la conexión Wi-Fi de Wokwi. Repetir la comprobación en vivo antes de afirmar que siguen entrando datos.

Cerrar indicando con claridad que falta la evidencia de una instalación **Ubuntu local separada**, además de la presentación y la entrega oficial. La versión AWS usa HTTP sin HTTPS y un broker MQTT público de pruebas, adecuado solo para este prototipo simulado.

**Enlaces para preparar la demostración:** [Repositorio](https://github.com/nathernandez1189/savia-iot) · [Wokwi](https://wokwi.com/projects/477744536654042113) · [Tablero](https://nathernandez1189.github.io/savia-iot/) · [Checklist](../CHECKLIST_ENTREGA_PRACTICA_1.md).