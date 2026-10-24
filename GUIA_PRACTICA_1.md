# Guía de la Práctica 1 | Savia IoT

**Materia:** Inteligencia Artificial Aplicada a Internet de las Cosas  
**Docente:** Jhorman Andrés Villanueva Vivas  
**Integrantes:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés.

## Caso y recorrido de las lecturas

El [ESP32 con DHT22 simulado en Wokwi](https://wokwi.com/projects/477744536654042113) representa un invernadero de tomates. El sensor mide temperatura y humedad relativa del **aire**; no mide suelo ni estado de las plantas. El ESP32 publica lecturas por MQTT. Un puente en la VM Ubuntu recibe ese canal y entrega cada mensaje a la aplicación Python por HTTP local. La aplicación valida y deduplica antes de guardar en PostgreSQL y generar el CSV.

    DHT22 → ESP32 → MQTT → puente en Ubuntu → aplicación Python
                                             ├→ PostgreSQL
                                             └→ CSV

La ventilación es una regla del ESP32: en AUTO enciende un LED por encima de 30 °C y lo apaga por debajo de 27 °C. El LED **representa** el actuador; no hay un ventilador físico conectado. El tablero publicado en [GitHub Pages](https://nathernandez1189.github.io/savia-iot/) es una interfaz separada. El clima de Open-Meteo es exterior e informativo y no reemplaza lecturas del DHT22.

El broker MQTT usado en la práctica es público y no autentica quién envía un mensaje. El token para escribir en la aplicación permanece en el servidor, fuera del código público de Wokwi. Esta configuración solo se utiliza con datos simulados.

## Segunda parte: despliegue AWS

La plantilla [aws/savia-iot.yaml](aws/savia-iot.yaml) crea en AWS Academy Learner Lab una VPC, una subred pública para EC2 Ubuntu, dos subredes privadas para RDS PostgreSQL, una IP elástica y grupos de seguridad. La base no es pública y acepta el puerto 5432 solamente desde el grupo de la VM. La instancia usa el perfil propio del Learner Lab; en otra cuenta hay que adaptar ese perfil y revisar la configuración antes de desplegar.

El 24 de octubre de 2026 se comprobó que la pila estaba en CREATE_COMPLETE, EC2 y RDS estaban disponibles, y la ruta de salud devolvía estado correcto con PostgreSQL. Durante una sesión de Wokwi, el contador pasó de 4 a 13 lecturas; las secuencias 23–25 coincidieron en la API y el CSV. Esto respalda esa sesión de prueba, no una conexión continua. La [evidencia detallada](entregables/Evidencia_AWS_2026-10-24.md) registra también una segunda prueba en la que falló la pasarela Wi-Fi de Wokwi y no llegaron nuevos mensajes.

El servidor expone HTTP sin HTTPS. Su IP es temporal y solo funciona mientras el laboratorio permanezca activo; por eso no se usa aquí como enlace permanente de entrega.

## Reproducción de la etapa inicial en Ubuntu local

Además de la VM Ubuntu de AWS, el 24 de octubre se ejecutó el servidor en **Ubuntu 24.04 local mediante Docker**. La [evidencia local](entregables/Evidencia_Ubuntu_Local_2026-10-24.md) registra cuatro lecturas del ESP32 simulado recibidas en SQLite y CSV. Para repetirla en un equipo con Git y Docker Desktop:

~~~bash
git clone https://github.com/nathernandez1189/savia-iot.git
cd savia-iot
docker build -f local-ubuntu/Dockerfile -t savia-iot-ubuntu-local:practica1 .
docker run --rm savia-iot-ubuntu-local:practica1 python3 -m unittest discover -s server -p 'test_*.py' -v
mkdir -p server/data
docker run -d --rm --name savia-ubuntu-local -p 127.0.0.1:18000:8000 -e SAVIA_DEVICE_TOKEN=TOKEN_DE_PRUEBA -v "$PWD/server/data:/data" savia-iot-ubuntu-local:practica1
~~~

Abrir la simulación en Wokwi y verificar que el monitor serial indique `MQTT conectado`. En otra terminal, iniciar temporalmente el puente en el mismo contenedor:

~~~bash
docker exec -e SAVIA_DEVICE_TOKEN=TOKEN_DE_PRUEBA savia-ubuntu-local python3 server/mqtt_bridge.py
~~~

Después de varias lecturas, consultar `http://127.0.0.1:18000/health` y `http://127.0.0.1:18000/api/readings.csv`. La tabla `readings` queda en `server/data/readings.sqlite3`. El token de este ejemplo es solo para una prueba local; reemplazarlo por otro valor y no publicarlo como credencial de un servidor expuesto. El puente debe permanecer abierto durante la demostración. Para detener el contenedor: `docker stop savia-ubuntu-local`.

## Secuencia para la sustentación

1. Mostrar el caso de uso y el circuito en [Wokwi](https://wokwi.com/projects/477744536654042113); variar el DHT22 y explicar la regla local.
2. Verificar que el monitor serial indique conexión antes de afirmar que hay envío remoto. Si falla la red, mostrar solo el control local y explicar el límite.
3. En AWS, mostrar la VM pública, las subredes privadas de RDS y sus grupos de seguridad sin enseñar claves.
4. Comparar una lectura identificada por el mismo arranque y secuencia en la API, el CSV y PostgreSQL.
5. Comparar las secuencias del mismo arranque en Ubuntu local (SQLite/CSV) y AWS (PostgreSQL/CSV).

La [ficha de implementación y evidencia](CHECKLIST_ENTREGA_PRACTICA_1.md) resume qué se observó en cada componente y el alcance de esas comprobaciones.
