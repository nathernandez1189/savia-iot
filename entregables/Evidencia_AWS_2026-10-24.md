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

En una **segunda sesión del mismo 24 de octubre**, Wokwi recuperó su conexión Wi-Fi y MQTT. El contador de AWS pasó de **13 a 23** registros. Las secuencias **23 y 24** del arranque `8b9a8e13`, con **26,0 °C y 65,0 %**, aparecieron tanto en la API respaldada por PostgreSQL como en el CSV. Esas mismas secuencias se recibieron también en la ejecución [Ubuntu local](Evidencia_Ubuntu_Local_2026-10-24.md). La recepción no fue continua: el broker público y el simulador presentaron interrupciones durante las pruebas.

## Límites de la comprobación

Entre las dos sesiones, Wokwi mostró un error al conectarse a su pasarela Wi-Fi en dos navegadores. El ESP32 mantuvo el control local; más tarde la conexión se recuperó. La segunda sesión confirmó de nuevo el recorrido completo, pero **no acredita disponibilidad continua**. Para la sustentación conviene repetirlo en vivo y conservar capturas legibles del simulador, la API y el CSV.

Además de la VM Ubuntu de AWS, la aplicación y el puente se ejecutaron y comprobaron en un [Ubuntu local separado](Evidencia_Ubuntu_Local_2026-10-24.md). Sus datos de prueba se guardaron en SQLite y CSV; AWS utilizó PostgreSQL y CSV.

Los datos del DHT22 son simulados. El broker MQTT público no autentica la procedencia de un mensaje; por eso este montaje no se presenta como una instalación productiva. El servidor AWS ofrece HTTP sin HTTPS y su dirección pública es temporal. El clima exterior de Open-Meteo en el tablero es una fuente distinta y no se usa como lectura del invernadero.

[Consultar la ficha de implementación y evidencia](../CHECKLIST_ENTREGA_PRACTICA_1.md).
