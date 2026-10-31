# Savia IoT · Contexto de mantenimiento

Lee [00-indice.md](00-indice.md) y [decisiones.md](decisiones.md) antes de modificar el proyecto.

## Proyecto

Prototipo académico de la UAO: ESP32 y DHT22 simulados en Wokwi miden temperatura y humedad del aire. El LED representa ventilación con histéresis: ON por encima de 30 °C, OFF por debajo de 27 °C. No hay modelo de IA entrenado ni mediciones físicas de plantas.

Equipo: Natalia Hernández, Sidney Leusson, José Luque y Jarvin Alvarado.

## Estructura

- `practica-1/`: Wokwi, servidor Python, puente MQTT→HTTP, PostgreSQL/SQLite, CSV, Docker local, CloudFormation y evidencias.
- `practica2/`: Mosquitto autenticado, colector, cola SQLite, InfluxDB, Grafana, firmware y evidencias. **Conservar este nombre y esta carpeta**, por petición de Natalia.
- `dashboard/`: React/Vite, pruebas, recursos originales y fuente de GitHub Pages.
- `proyecto-final/`: espacio de trabajo futuro; no declarar modelos o resultados inexistentes.
- `.github/workflows/`: pruebas y publicación de Pages.

## Reglas

- Nunca versionar claves reales, tokens, `.env`, llaves AWS o datos privados. Mantener ejemplos con marcadores. En el Wokwi público de la Práctica 2, conservar `CAMBIAR_POR_CLAVE_TEMPORAL`.
- Distinguir el broker público de la Práctica 1 (actualmente `broker.emqx.io`) de Mosquitto propio en la Práctica 2. Los brokers públicos sirven solo para datos simulados, nunca para controlar equipos físicos.
- Conservar los resultados, fechas y límites de las evidencias. Al moverlas se pueden corregir enlaces relativos, sin reescribir los hechos observados.
- No cambiar la infraestructura AWS ni generar costes como efecto de una tarea de documentación o limpieza. Toda operación debe estar dentro de la solicitud del usuario.
- No reescribir historial ni descartar trabajo ajeno. Para una eliminación material no autorizada o una operación irreversible, solicitar aprobación con el alcance concreto.
- Las rutas del repositorio y las de ejecución en la VM son distintas: los `.service` usan `/opt/savia-iot/server`; no alterarlas solo porque el código esté en `practica-1/server`.
- GitHub Pages se construye desde `dashboard/`. No copiar `dist/` a la raíz. Verificar la publicación y el enlace a Wokwi después de cambios que los afecten.
- Los PDF y PowerPoint se distribuyen en Releases; verificar la copia antes de retirar un entregable del código. No elegir una licencia sin decisión del equipo.

## Comprobaciones

Desde la raíz, instalar dependencias Python en un entorno virtual y ejecutar:

```bash
python -m pip install -r practica-1/server/requirements.txt -r practica2/requirements.txt
python -m unittest discover -s practica-1/server -p 'test_*.py' -v
python -m unittest discover -s practica2 -p 'test_*.py' -v
```

Desde `dashboard/`: `npm ci`, `npm run check`, `npm test` y `npm run build`. El contenedor local se construye desde la raíz con `docker build -f practica-1/local-ubuntu/Dockerfile -t savia-iot-ubuntu-local:practica1 practica-1`.

Documentar en español y hacer commits pequeños en español. Registrar decisiones de arquitectura y actualizar el índice al cerrar un hito. Una prueba local, una captura o un despliegue de Pages no acreditan por sí solos recepción de telemetría en AWS.
