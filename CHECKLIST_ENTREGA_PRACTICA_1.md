# Estado de la Práctica 1 | Savia IoT

**Asignatura:** Inteligencia Artificial Aplicada a Internet de las Cosas  
**Docente:** Jhorman Andrés Villanueva Vivas  
**Equipo:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés  
**Verificación:** 24 de octubre de 2026  
**Fuente:** enunciado «Práctica 1: Servidor web para un proyecto de IoT».

| Requisito del enunciado | Estado comprobado |
|---|---|
| 1. Caso de monitoreo de temperatura y humedad | **Realizado.** Invernadero de tomates; DHT22 simulado mide aire interior en [Wokwi](https://wokwi.com/projects/477744536654042113). |
| 2. Aplicación web en servidor Ubuntu local | **Pendiente de evidencia.** El servidor funciona en AWS y la prueba automatizada pasó en macOS, pero no se documentó una instalación Ubuntu local separada. |
| 3. Envío de datos del ESP32 a la aplicación | **Comprobado en una sesión.** El ESP32 publicó por MQTT y un puente en la VM entregó las lecturas a la aplicación Python; el contador en AWS pasó de 4 a 13. No es envío HTTP directo desde el ESP32. |
| 4. Almacenamiento en CSV y base de datos | **Comprobado en AWS.** Las mismas secuencias aparecieron en la API respaldada por PostgreSQL y en CSV. Falta repetir y registrar la prueba en Ubuntu local. |
| 5. VM en AWS, servidor público, base privada, IP elástica y reglas de acceso | **Comprobado el 24 de octubre.** La pila CloudFormation quedó en CREATE_COMPLETE; EC2 estaba en ejecución y RDS no tenía acceso público. |
| 6. Proyecto en GitHub y enlace compartido | **Repositorio publicado.** [Enlace para compartir](https://github.com/nathernandez1189/savia-iot). Compartirlo con el docente o subirlo al campus requiere la acción del equipo. |
| 7. Presentación a los compañeros | **Pendiente.** Existe un [esquema de exposición](entregables/Guion_Exposicion_AWS.md), pero no se ha constatado la sustentación. |

## Qué conviene cerrar antes de entregar

1. Ejecutar el servidor en una instalación Ubuntu **local separada** y guardar evidencia de una lectura en la base y en el CSV. La [guía](GUIA_PRACTICA_1.md) incluye los pasos.
2. Repetir una demostración en vivo del recorrido Wokwi → MQTT → aplicación → PostgreSQL/CSV. En la segunda comprobación del 24 de octubre, la pasarela Wi-Fi de Wokwi no conectó y no produjo lecturas nuevas; el ESP32 sí mantuvo el control local.
3. Preparar la exposición y realizar la entrega por el canal indicado por el docente. Publicar el repositorio no equivale a entregarlo oficialmente.

**Alcance de la evidencia:** los datos proceden de una simulación, no de un cultivo real. El LED representa la ventilación. El clima exterior del tablero procede de Open-Meteo y no es una lectura del ESP32. El broker MQTT de pruebas es público; la prueba no acredita autenticación del origen ni disponibilidad continua. [Resultados observados](entregables/Evidencia_AWS_2026-10-24.md).