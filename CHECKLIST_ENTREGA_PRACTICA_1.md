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
| Aplicación web en Ubuntu local | Aplicación Python ejecutada en **Ubuntu 24.04 local mediante Docker**, separada de AWS. Expone salud, API y CSV. Recibió cuatro lecturas de Wokwi por el puente MQTT; las secuencias 22–25 quedaron en SQLite y CSV. [Evidencia local](entregables/Evidencia_Ubuntu_Local_2026-10-24.md). |
| Comunicación del dispositivo | El ESP32 publica las lecturas por MQTT. Un puente en cada Ubuntu las entrega por HTTP local a su aplicación. AWS pasó de 4 a 13 lecturas en una sesión y de 13 a 23 en otra; el Ubuntu local recibió las secuencias 22–25 del segundo arranque. La configuración activa no usa envío HTTP directo desde el ESP32. |
| Persistencia | La aplicación valida y deduplica los mensajes. Las secuencias 23–25 de un mismo arranque coincidieron en la API respaldada por PostgreSQL y en el CSV del servidor. |
| Infraestructura AWS | La pila CloudFormation llegó a CREATE_COMPLETE. Incluye EC2 Ubuntu en subred pública con IP elástica, PostgreSQL RDS en subredes privadas y grupos de seguridad que restringen el acceso a la base. La [plantilla](aws/savia-iot.yaml) permite examinar la configuración. |
| Código y demostración | [Repositorio GitHub](https://github.com/nathernandez1189/savia-iot), [simulación Wokwi](https://wokwi.com/projects/477744536654042113), [tablero Savia IoT](https://nathernandez1189.github.io/savia-iot/) y [presentación](entregables/Savia_IoT_Practica_1_AWS.pptx). |

El [código fuente del tablero](dashboard/) también está incluido. Pasó la comprobación de tipos y 12 pruebas; su compilación reproduce los archivos HTML, CSS y JavaScript de la versión publicada.

## Estado frente a los siete puntos del enunciado

Los puntos **1 a 6** cuentan con implementación y evidencia técnica: caso de uso, servidor Ubuntu local, telemetría del ESP32 simulado, CSV y base de datos, despliegue AWS y repositorio GitHub. El punto **7**, presentación frente a los compañeros, tiene [diapositivas](entregables/Savia_IoT_Practica_1_AWS.pptx) preparadas; la exposición solo puede marcarse realizada después de presentarla. El informe y las diapositivas están en [entregables/](entregables/) para revisión del equipo antes de subirlos a CampusDigital.

## Alcance de la evidencia

El enunciado distingue la configuración inicial de un servidor Ubuntu y la posterior implementación en AWS. Se ejecutó **Ubuntu local en un contenedor Docker** y, por separado, una **VM Ubuntu en AWS**. La primera guardó SQLite y CSV; la segunda, PostgreSQL y CSV. Las [evidencias local](entregables/Evidencia_Ubuntu_Local_2026-10-24.md) y [AWS](entregables/Evidencia_AWS_2026-10-24.md) registran los resultados de cada entorno.

La recepción desde Wokwi se observó en dos sesiones de AWS y una de Ubuntu local. Entre ellas, la pasarela Wi-Fi de Wokwi falló temporalmente y luego se recuperó. En la segunda sesión de AWS, el contador pasó de **13 a 23**; las secuencias 23 y 24 del arranque `8b9a8e13` coincidieron con las recibidas en Ubuntu local. Estos son resultados fechados, no una garantía de conexión permanente. El broker MQTT es público y se usa únicamente con datos simulados.

El DHT22 no mide humedad del suelo, pH ni nutrientes; el LED no es un ventilador físico. El clima exterior que muestra el tablero procede de Open-Meteo y no reemplaza lecturas interiores. La [evidencia técnica del 24 de octubre](entregables/Evidencia_AWS_2026-10-24.md) amplía los resultados y sus límites.
