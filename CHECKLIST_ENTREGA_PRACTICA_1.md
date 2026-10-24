# Práctica 1 | Implementación y evidencia de Savia IoT

**Asignatura:** Inteligencia Artificial Aplicada a Internet de las Cosas  
**Docente:** Jhorman Andrés Villanueva Vivas  
**Integrantes:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés  
**Fecha de la comprobación técnica:** 24 de octubre de 2026

## Caso de uso

Savia IoT representa el monitoreo de un invernadero de tomates. Un ESP32 y un DHT22 simulados en [Wokwi](https://wokwi.com/projects/477744536654042113) generan lecturas de temperatura y humedad relativa del **aire**. El ESP32 conserva el control local de un LED que representa la ventilación: se activa por encima de 30 °C y se desactiva por debajo de 27 °C.

## Componentes desarrollados y comprobaciones

| Componente | Implementación y evidencia |
|---|---|
| Aplicación web en Ubuntu | Aplicación Python ejecutada en una **VM Ubuntu de AWS Academy Learner Lab**. Expone una ruta de salud, una API de lecturas y una descarga CSV. Su código está en [server/](server/). |
| Comunicación del dispositivo | El ESP32 publica las lecturas por MQTT. Un puente en la VM las entrega por HTTP local a la aplicación. Durante una sesión comprobada, el contador pasó de 4 a 13 lecturas. La configuración activa no usa envío HTTP directo desde el ESP32. |
| Persistencia | La aplicación valida y deduplica los mensajes. Las secuencias 23–25 de un mismo arranque coincidieron en la API respaldada por PostgreSQL y en el CSV del servidor. |
| Infraestructura AWS | La pila CloudFormation llegó a CREATE_COMPLETE. Incluye EC2 Ubuntu en subred pública con IP elástica, PostgreSQL RDS en subredes privadas y grupos de seguridad que restringen el acceso a la base. La [plantilla](aws/savia-iot.yaml) permite examinar la configuración. |
| Código y demostración | [Repositorio GitHub](https://github.com/nathernandez1189/savia-iot), [simulación Wokwi](https://wokwi.com/projects/477744536654042113), [tablero Savia IoT](https://nathernandez1189.github.io/savia-iot/) y [esquema de exposición](entregables/Guion_Exposicion_AWS.md). |

## Alcance de la evidencia

El enunciado distingue la configuración inicial de un servidor Ubuntu y la posterior implementación en AWS. **Las comprobaciones fechadas de este documento corresponden a la VM Ubuntu de AWS**; la [guía de reproducción](GUIA_PRACTICA_1.md) describe cómo ejecutar el servidor en un Ubuntu local fuera de AWS. Esa guía es un procedimiento y no constituye, por sí sola, evidencia de una segunda ejecución.

La recepción desde Wokwi se observó durante una sesión. En una comprobación posterior del mismo día, la pasarela Wi-Fi de Wokwi no conectó y no produjo nuevas filas, aunque el control local del ESP32 funcionó. Por eso las cifras anteriores se presentan como resultados fechados, no como garantía de conexión permanente. El broker MQTT es público y se usa únicamente con datos simulados.

El DHT22 no mide humedad del suelo, pH ni nutrientes; el LED no es un ventilador físico. El clima exterior que muestra el tablero procede de Open-Meteo y no reemplaza lecturas interiores. La [evidencia técnica del 24 de octubre](entregables/Evidencia_AWS_2026-10-24.md) amplía los resultados y sus límites.