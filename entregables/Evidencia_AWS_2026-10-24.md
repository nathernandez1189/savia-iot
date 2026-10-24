# Evidencia de la Práctica 1 | AWS

**Fecha de comprobación:** 24 de octubre de 2026  
**Materia:** Inteligencia Artificial Aplicada a Internet de las Cosas  
**Docente:** Jhorman Andrés Villanueva Vivas  
**Equipo:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés.

## Montaje examinado

En [Wokwi](https://wokwi.com/projects/477744536654042113), un ESP32 lee un DHT22 que simula la temperatura y la humedad relativa del aire de un invernadero de tomates. El ESP32 publica telemetría por MQTT. En AWS Academy Learner Lab, un puente MQTT ejecutado en una VM Ubuntu entrega las lecturas a una aplicación Python, que valida los mensajes y los almacena en PostgreSQL RDS y CSV. Un LED representa la ventilación controlada localmente por el ESP32.

La infraestructura descrita en [CloudFormation](../aws/savia-iot.yaml) incluye una VM en subred pública, dos subredes privadas para RDS, IP elástica y grupos de seguridad. No se expuso RDS a Internet; el puerto de PostgreSQL estaba permitido solo desde el grupo de la VM.

## Resultados observados

| Comprobación | Resultado del 24 de octubre |
|---|---|
| Infraestructura | La pila CloudFormation quedó en CREATE_COMPLETE con 16 recursos; EC2 estaba en ejecución y RDS disponible y sin acceso público. |
| Servicio | La aplicación, el puente MQTT y Nginx estaban activos; la ruta de salud devolvió estado correcto y señaló PostgreSQL. |
| Recepción | En una sesión de Wokwi, el contador de la aplicación pasó de 4 a 13 lecturas. |
| Persistencia | Las secuencias 23, 24 y 25 de un mismo arranque, con 24,0 °C y 65,0 % de humedad, coincidieron en la API y el CSV. El CSV del servidor tenía 13 filas de datos más su encabezado. |
| Control local | En una prueba posterior, 32 °C activó el indicador en AUTO y 26 °C lo desactivó. Los botones de encender, apagar y volver a automático cambiaron el estado. |
| Tablero | El sitio público abrió; una lectura del historial permaneció tras recargar y se descargó como CSV. |

La coincidencia de identificadores y valores respalda que esas lecturas llegaron a la aplicación y quedaron disponibles en PostgreSQL y CSV durante la sesión observada. El repositorio no contiene un volcado de la base ni datos reales de un cultivo.

## Límites de la comprobación

Más tarde, el mismo 24 de octubre, Wokwi mostró un error al conectarse a su pasarela Wi-Fi en dos navegadores. El ESP32 mantuvo el control local, pero el contador de AWS permaneció en 13. Por tanto, **no se afirma que el flujo completo esté conectado en este momento** ni que haya mantenido disponibilidad durante varios días. Antes de la sustentación se debe repetir la prueba de extremo a extremo y guardar capturas de Wokwi, API, CSV y PostgreSQL.

La aplicación se comprobó con una prueba automatizada en macOS para validación, deduplicación y persistencia SQLite/CSV. La infraestructura y los datos observados en este informe corresponden a la VM Ubuntu de AWS. El procedimiento para una ejecución Ubuntu local, fuera de AWS, se presenta por separado en la guía del proyecto.

Los datos del DHT22 son simulados. El broker MQTT público no autentica la procedencia de un mensaje; por eso este montaje no se presenta como una instalación productiva. El servidor AWS ofrece HTTP sin HTTPS y su dirección pública es temporal. El clima exterior de Open-Meteo en el tablero es una fuente distinta y no se usa como lectura del invernadero.

[Consultar la ficha de implementación y evidencia](../CHECKLIST_ENTREGA_PRACTICA_1.md).