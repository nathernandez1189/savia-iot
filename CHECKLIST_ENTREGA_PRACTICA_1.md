# Savia IoT - checklist de la Práctica 1

**Materia:** Inteligencia Artificial aplicada a Internet de las Cosas

**Docente:** Jhorman Andrés Villanueva Vivas

**Estado comprobado:** 17 de octubre de 2026

**Base:** enunciado «Práctica 1 - Servidor web para un proyecto de IoT».

## Listo y comprobado

- [x] Caso de uso: temperatura y humedad del aire en un invernadero de tomates.
- [x] ESP32 y DHT22 simulados en [Wokwi](https://wokwi.com/projects/477744536654042113), con lectura y control local de ventilación simulada.
- [x] Aplicación web Python ejecutada en una VM Ubuntu de Azure. La [ruta de salud](https://23-101-172-173.sslip.io/health) respondió con `status: ok` y `database: postgres` durante la verificación.
- [x] Publicación de lecturas por MQTT desde Wokwi. El puente de la VM entrega esos mensajes a la aplicación web local; ningún token está incluido en el código público del ESP32.
- [x] Misma sesión y lectura de Wokwi confirmadas en PostgreSQL y `readings.csv`: `boot=a4cb5ad6`, `seq=6`, 24,0 °C y 65,0 %.
- [x] VM en subred pública, PostgreSQL en subred privada, IP pública estática y reglas NSG. El docente acepta Azure según la confirmación de la estudiante; estos son los equivalentes funcionales de los elementos AWS nombrados en el enunciado.
- [x] Código y guía en este repositorio; presentación y [evidencia de funcionamiento](entregables/Evidencia_Savia_IoT_Azure_2026-10-17.pdf) disponibles para el equipo.

## Antes de exponer o entregar

- [ ] Documentar por separado la **primera parte local en Ubuntu**. El servidor ya pasó pruebas locales con SQLite, pero no se ha documentado una ejecución local Ubuntu distinta de la VM de Azure. Confirmar si el docente acepta la VM para ese punto o hacer la demostración separada.
- [ ] Explicar la ruta Wokwi → MQTT → puente → aplicación web. Consultar si el profesor exige que el ESP32 haga HTTP directo a la aplicación; el enunciado no fija el protocolo, pero pide modificar el código del dispositivo para enviar datos a la aplicación web.
- [ ] Mostrar en clase el monitor serial, los registros del servidor, PostgreSQL, CSV y la red pública/privada. La evidencia actual verifica una ejecución puntual, no disponibilidad prolongada.
- [ ] Presentar el trabajo ante los compañeros y confirmar la entrega en la plataforma académica. Tener las diapositivas listas no equivale a haberlas presentado o subido.
- [ ] Confirmar si se exige montaje físico con ESP32 y DHT22. Lo verificado aquí es una simulación.
- [ ] Después de la clase del 24 de octubre de 2026, guardar la evidencia necesaria y retirar los recursos de Azure para evitar cargos posteriores.

**Límite:** el broker MQTT es público y no autentica el origen del mensaje; los datos son simulados y no deben interpretarse como mediciones reales de un cultivo.
