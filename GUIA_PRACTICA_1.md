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

## Primera parte: verificación pendiente en Ubuntu local

La ejecución automatizada del servidor se probó en macOS, pero todavía **falta ejecutar y documentar** una instalación Ubuntu local separada, como solicita el enunciado. En esa máquina, con Python 3 y Git instalados, el equipo puede iniciar una prueba local con SQLite y CSV:

~~~bash
git clone https://github.com/nathernandez1189/savia-iot.git
cd savia-iot
python3 -m unittest discover -s server -p 'test_*.py' -v
mkdir -p server/data
SAVIA_HOST=127.0.0.1 SAVIA_DB_KIND=sqlite SAVIA_DATA_DIR="$PWD/server/data" SAVIA_DEVICE_TOKEN=TOKEN_DE_PRUEBA python3 server/app.py
~~~

En otra terminal, sustituir el token de ejemplo por el mismo valor elegido arriba y enviar una muestra de prueba:

~~~bash
curl -i http://127.0.0.1:8000/api/telemetry -H 'Content-Type: application/json' -H 'X-Device-Token: TOKEN_DE_PRUEBA' -d '{"boot":"PRUEBA01","seq":1,"ts":1791633600000,"temperature":31.2,"humidity":64.5,"mode":"AUTO","fan":true,"alarm":"NORMAL","reason":"lectura"}'
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/readings.csv
~~~

La petición manual comprueba el servidor y sus salidas, pero **no** que el ESP32 haya enviado esa muestra. Para completar la primera parte, conectar Wokwi a esa instalación mediante el puente MQTT o una ruta alcanzable y documentar que la lectura del dispositivo llega tanto a SQLite como a CSV. Conservar capturas legibles de Ubuntu, Wokwi y las dos salidas.

## Secuencia para la sustentación

1. Mostrar el caso de uso y el circuito en [Wokwi](https://wokwi.com/projects/477744536654042113); variar el DHT22 y explicar la regla local.
2. Verificar que el monitor serial indique conexión antes de afirmar que hay envío remoto. Si falla la red, mostrar solo el control local y explicar el límite.
3. En AWS, mostrar la VM pública, las subredes privadas de RDS y sus grupos de seguridad sin enseñar claves.
4. Comparar una lectura identificada por el mismo arranque y secuencia en la API, el CSV y PostgreSQL.
5. Exponer la fase local Ubuntu cuando exista su evidencia y entregar el repositorio por el canal indicado por el docente.

La presentación, la prueba local Ubuntu y la subida al campus se registran como pendientes en el [estado de la práctica](CHECKLIST_ENTREGA_PRACTICA_1.md).