# Evidencia técnica · Savia IoT en AWS

**Fecha de observación:** 24 de octubre de 2026 (UTC).  
**Materia:** Inteligencia Artificial Aplicada a Internet de las Cosas.  
**Equipo:** Natalia Hernández Piedrahita, Sidney Leonardo Leusson Angulo, José Fernando Luque Cajiao y Jarvin David Alvarado Garcés.  
**Docente:** Jhorman Andrés Villanueva Vivas.

## Caso y recorrido de los datos

Se simuló un invernadero de tomates con un ESP32 y un DHT22 en [Wokwi](https://wokwi.com/projects/477744536654042113). El sensor representa temperatura y humedad relativa **del aire interior**. El ESP32 publica la telemetría por MQTT. En AWS, un puente ejecutado en la VM Ubuntu escucha el canal y remite las lecturas a la aplicación Python. Esta valida cada mensaje y lo guarda en dos destinos: PostgreSQL RDS y CSV. El modo AUTO controla localmente un LED que representa el ventilador. La aplicación [Savia IoT](https://nathernandez1189.github.io/savia-iot/) permite observar el prototipo; el clima de Open-Meteo, cuando se consulta, es exterior e informativo.

## Infraestructura observada

- Cuenta AWS Academy Learner Lab; región `us-east-1`; pila CloudFormation `savia-iot-lab` con **16 recursos en CREATE_COMPLETE**.
- VM EC2 Ubuntu `i-01f3188a0db02ef65`, observada en estado `running`, con IP elástica `184.193.138.254` en la subred pública.
- Base RDS PostgreSQL `savia-iot-db` en subredes privadas; `PubliclyAccessible=False`.
- Grupo de seguridad de la base: acceso a 5432 solo desde el grupo del servidor web.
- Servicios de aplicación, puente MQTT y Nginx comprobados activos en la instancia durante la preparación del laboratorio.

## Pruebas realizadas

| Evidencia | Resultado |
|---|---|
| `GET http://184.193.138.254/health` desde AWS CloudShell | `status=ok`, `database=postgres` |
| Contador de lecturas durante la simulación | Pasó de **4 a 13**; demuestra llegada de varias muestras durante una sesión |
| `GET /api/readings?limit=3` | Últimas secuencias `23`, `24` y `25` del arranque `465479e7` |
| `GET /api/readings.csv` | Las mismas secuencias `23`, `24`, `25` con 24.0 °C y 65.0 % |
| DNS de `184-193-138-254.sslip.io` | Resolvió a `184.193.138.254`; no implica que exista HTTPS |
| Programación de retiro | `savia-iot-cleanup-2026-11-01`: habilitada para el 1 de noviembre de 2026 a las 23:00 en `America/Bogota` |

El conteo procede de PostgreSQL porque la aplicación estaba configurada con `SAVIA_DB_KIND=postgres`. La igualdad de identificadores y valores entre API y CSV comprueba que ambas salidas contienen las mismas muestras observadas. La verificación es de una sesión; no constituye una prueba de funcionamiento por varios días ni autentica el origen de un mensaje en el broker público.

## Qué enseñar durante la exposición

1. En Wokwi: circuito ESP32/DHT22, monitor serial, temperatura y humedad, y reacción del LED al superar los umbrales.
2. En CloudFormation: recursos `WebServer`, `Database`, `ElasticIP`, `PublicSubnet` y `PrivateSubnetA/B`.
3. En el servidor: `/health`, `/api/readings` y `/api/readings.csv`; comparar un mismo `boot` y `seq`.
4. Explicar que el servidor está en red pública y RDS solo en red privada; no mostrar contraseñas ni parámetros privados.

## Verificación local de código

Se ejecutó la prueba automatizada del servidor en el Mac del equipo: 1 prueba aprobada. Verificó autenticación, rechazo de lecturas inválidas, deduplicación y persistencia en SQLite y CSV. Esta prueba **no equivale** a una instalación local Ubuntu: Docker Desktop no respondió a la comprobación y no se pudo abrir un contenedor Ubuntu en esta sesión.

## Estado para la entrega

La **fase AWS** está desplegada y las lecturas de Wokwi llegaron a PostgreSQL y CSV. Para afirmar que toda la práctica está terminada falta documentar una **prueba local separada en Ubuntu** si el profesor la exige y presentar/subir oficialmente el material. El acceso HTTP desde CloudShell funcionó; Chrome bloqueó por el cliente tanto la IP como el nombre gratuito `184-193-138-254.sslip.io`; el navegador interno sí abrió la IP. No se ha instalado HTTPS en AWS. [Checklist vigente](../CHECKLIST_ENTREGA_PRACTICA_1.md).

## Segunda comprobación del 24 de octubre (14:26 UTC y minutos siguientes)

- EC2 siguió en `running`; los chequeos de instancia y sistema devolvieron `ok`. RDS estaba `available` y `PubliclyAccessible=False`.
- AWS Systems Manager confirmó `active` para `savia-iot`, `savia-mqtt` y `nginx`. En la VM, `readings.csv` tenía 14 líneas: un encabezado y 13 lecturas.
- El navegador interno abrió `http://184.193.138.254/`, `/health` y `/api/readings?limit=2` correctamente. Chrome de esta sesión bloqueó HTTP, por lo que el problema de Chrome no equivale a un fallo de AWS.
- Las pruebas locales automatizadas pasaron nuevamente (1 prueba), cubriendo autenticación, deduplicación, validación y SQLite/CSV.
- El ESP32 de Wokwi leyó el DHT22. A 32 °C encendió el indicador en AUTO; a 26 °C lo apagó. Los botones Encender, Apagar y Auto cambiaron el estado como se esperaba.
- **Bloqueo actual de red:** dos navegadores mostraron `WiFi Error: Connection to IoT Gateway wss://netwi.wokwi.com/ failed`. El monitor serial quedó en `RED=LOCAL`; el contador AWS permaneció en 13. No se atribuye la causa sin un diagnóstico adicional y no se afirma una nueva transmisión de Wokwi a AWS en esta segunda sesión.
- El dashboard público abrió. Su historial conservó una lectura al recargar y la exportación produjo un CSV con esa lectura. La búsqueda Open-Meteo devolvió Santiago de Cali con Valle del Cauca y Colombia, diferenciándola de homónimos. No se seleccionó una ubicación para no atribuir al cultivo una ciudad no indicada por el equipo, por lo que el pronóstico de siete días no se probó.

## Control de costos

Natalia autorizó un gasto máximo de USD 15 y pidió mantener el laboratorio hasta el 1 de noviembre. La retirada de la pila y de los dos parámetros privados quedó programada para esa fecha. Es imprescindible revisar el gasto y confirmar la eliminación efectiva después; una programación no es un límite automático de facturación. No incluir credenciales en capturas o entregables.
