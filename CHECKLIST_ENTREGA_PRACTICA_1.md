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
- [ ] Confirmar en el navegador de la estudiante el acceso remoto a la VM. AWS CloudShell sí respondió por HTTP; Chrome mostró antes un bloqueo del cliente al abrir la IP. El servidor no tiene HTTPS.
- [ ] Capturar una prueba completa en la sustentación: Wokwi, monitor serial, API, CSV y una consulta PostgreSQL sin secretos.
- [ ] Presentar y subir el material al campus. Tener código y documentación en GitHub no equivale a entrega oficial.
- [ ] Aclarar si el profesor exige un montaje físico. Todo lo verificado utiliza una simulación, sin motor real.
- [ ] Tras el 1 de noviembre, comprobar que se borraron la pila, RDS, la IP elástica y los dos parámetros, y que no siguen los cargos.

**Límites:** los datos son simulados; el broker MQTT de pruebas es público y no autentica el origen. La página de GitHub Pages, el servidor AWS y el proyecto Wokwi son piezas distintas.
