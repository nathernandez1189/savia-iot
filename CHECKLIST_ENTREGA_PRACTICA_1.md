# Savia IoT · estado de la Práctica 1

**Materia:** Inteligencia Artificial Aplicada a Internet de las Cosas  
**Docente:** Jhorman Andrés Villanueva Vivas  
**Corte de verificación:** 24 de octubre de 2026  
**Base:** enunciado «Práctica 1 - Servidor web para un proyecto de IoT».

## Comprobado

- [x] Caso de uso del invernadero de tomates: temperatura y humedad del aire.
- [x] ESP32 y DHT22 simulados en [Wokwi](https://wokwi.com/projects/477744536654042113); regla local de ventilación con LED como actuador simulado.
- [x] Aplicación Python y puente MQTT en una VM **Ubuntu de AWS Academy Learner Lab**.
- [x] ESP32 publica por MQTT; el puente recibe las lecturas y las entrega a la aplicación web. El token del servidor no está en Wokwi ni en GitHub.
- [x] PostgreSQL RDS privado y CSV: la API reportó `database=postgres` y 13 lecturas; el CSV y la API mostraron `boot=465479e7`, `seq=23…25`, 24.0 °C y 65.0 %.
- [x] La cifra subió de 4 a 13 durante la misma simulación: evidencia de recepción continuada durante esa sesión, aunque no de disponibilidad prolongada.
- [x] VPC, subred pública para EC2, dos privadas para RDS, IP elástica y grupos de seguridad creados por la pila `savia-iot-lab` (16 recursos `CREATE_COMPLETE`).
- [x] Repositorio, plantilla y guía actualizados con el despliegue AWS. [Evidencia del 24 de octubre](entregables/Evidencia_AWS_2026-10-24.md).
- [x] Eliminación de la pila programada para el 1 de noviembre a las 23:00 (Bogotá), según la fecha indicada por Natalia.

## Falta para afirmar que está **todo** completo

- [ ] Ejecutar y **capturar** una instalación local separada en Ubuntu con SQLite y CSV, o confirmar explícitamente con el docente que la VM Ubuntu de AWS satisface también la primera fase. Los tests locales de Python no demuestran por sí solos ese requisito.
- [x] Acceso remoto a la VM comprobado desde el navegador interno: la portada, `/health` y `/api/readings?limit=2` abrieron y mostraron 13 lecturas en PostgreSQL. Chrome de esta sesión bloqueó HTTP; el servidor sigue sin HTTPS.
- [ ] Capturar una prueba completa **en vivo** en la sustentación: Wokwi, monitor serial, API, CSV y consulta PostgreSQL sin secretos. En la verificación posterior, Wokwi mostró `WiFi Error: Connection to IoT Gateway wss://netwi.wokwi.com/ failed` en Chrome y navegador interno; el control local sí funcionó, pero esa sesión no generó nuevas filas en AWS.
- [ ] Presentar y subir el material al campus. Tener código y documentación en GitHub no equivale a entrega oficial.
- [ ] Aclarar si el profesor exige un montaje físico. Todo lo verificado utiliza una simulación, sin motor real.
- [ ] Tras el 1 de noviembre, comprobar que se borraron la pila, RDS, la IP elástica y los dos parámetros, y que no siguen los cargos.

**Verificación adicional del 24 de octubre:** EC2 `running` con estado de instancia/sistema `ok`; RDS `available` y no pública; servicios `savia-iot`, `savia-mqtt` y `nginx` activos; CSV de AWS con 13 filas de datos más encabezado. El historial del dashboard persistió tras recargar y su exportación descargó un CSV con una lectura. La búsqueda de municipios distinguió Cali (Colombia) de homónimos; el pronóstico no se probó porque no se configuró una ubicación real del cultivo.

**Límites:** los datos son simulados; el broker MQTT de pruebas es público y no autentica el origen. La página de GitHub Pages, el servidor AWS y el proyecto Wokwi son piezas distintas.
