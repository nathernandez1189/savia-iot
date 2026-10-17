# Savia IoT · invernadero de tomates

Prototipo académico para observar la temperatura y la humedad del **aire** de un invernadero y demostrar el control de la ventilación. El dispositivo se simula en Wokwi con un ESP32 y un DHT22; la página permite consultar lecturas y el estado del sistema.

**Abrir:** [dashboard público](https://nathernandez1189.github.io/savia-iot/) · [simulación ESP32 en Wokwi](https://wokwi.com/projects/477744536654042113)

## Qué hay en este repositorio

- `index.html`, `assets/` y `brand/`: versión compilada de la demostración web publicada en GitHub Pages. Se conservan para que el enlace siga funcionando.
- [`wokwi/sketch.ino`](wokwi/sketch.ino): programa del ESP32 con lectura del DHT22, control local, mensajes MQTT y recuperación de lecturas recientes.
- [`wokwi/diagram.json`](wokwi/diagram.json): circuito de la simulación.
- [`wokwi/libraries.txt`](wokwi/libraries.txt): bibliotecas utilizadas por Wokwi.

La página del repositorio es una compilación lista para publicar; **el código fuente editable de esa página no está incluido en este repositorio**. El circuito y su programa sí están disponibles en archivos editables.

## Demostración paso a paso

1. Abre la simulación en Wokwi y pulsa **Iniciar simulación**.
2. Cambia la temperatura y la humedad del DHT22; observa la pantalla LCD, el monitor serial y los indicadores.
3. En modo automático, el indicador verde de ventilación se enciende por encima de **30 °C** y se apaga por debajo de **27 °C**. Entre ambos umbrales conserva su estado para evitar cambios continuos.
4. Prueba los botones **AUTO**, **ENCENDER** y **APAGAR**. El LED verde representa el actuador: no es un ventilador físico.
5. Abre el dashboard para consultar la lectura interior, el historial y los controles. La comunicación remota de esta demostración usa MQTT; puede depender del acceso del navegador y del broker público de pruebas.
6. Si quieres comprobar la respuesta ante una caída de red, envía `c` desde el monitor serial de Wokwi. La simulación corta Wi-Fi durante unos 20 segundos y conserva la lógica local.

> Para reproducir el circuito desde los archivos de este repositorio, crea un proyecto ESP32 en Wokwi y reemplaza su `sketch.ino`, `diagram.json` y `libraries.txt` por los de la carpeta `wokwi/`. El proyecto enlazado arriba ya los contiene.

## Arquitectura y datos

```text
DHT22 → ESP32 → Wi-Fi/MQTT → dashboard
          │                        │
          └─ regla local → relé → LED verde (ventilación simulada)
```

- **Interior:** las lecturas del DHT22 en Wokwi representan temperatura y humedad relativa del aire del prototipo simulado.
- **Exterior:** cuando la página presenta clima de Open-Meteo, se trata de una estimación meteorológica de la ubicación elegida por el usuario. No sustituye una lectura interior faltante.
- **Control:** el ESP32 ejecuta reglas locales. El modo manual remoto vuelve a automático después de tres minutos; ante una desconexión también se recupera el control automático.
- **Historial:** el ESP32 conserva hasta 720 muestras recientes en memoria RAM y puede reenviarlas al reconectar. Reiniciar la simulación borra ese búfer.

## Alcance y pendientes

Esta versión demuestra monitoreo y ventilación con **reglas**; todavía no incluye un modelo de inteligencia artificial entrenado ni evidencia de resultados en un cultivo real. El DHT22 no mide humedad del suelo, pH ni nutrientes. El LED es un indicador, no un motor conectado físicamente.

El reto de la asignatura también contempla organizar el montaje por equipo, definir el uso de ESP32-CAM y MPU6050 cuando corresponda, y validar un actuador real con una alimentación y etapa de potencia apropiadas. No conectes una carga física directamente a un pin del ESP32 ni uses el broker MQTT público para datos privados o equipos reales.

## Verificación realizada

En la versión local del prototipo se comprobaron lecturas simuladas, control remoto con confirmación, un corte de red de 20 segundos, recuperación de lecturas y exportación CSV. Esas pruebas locales no prueban por sí solas que un dispositivo físico o la página pública estén conectados en este momento. Para una exposición, vuelve a ejecutar los pasos anteriores y registra el resultado observado.

## Referencias técnicas

- [Wokwi: Wi-Fi con ESP32](https://docs.wokwi.com/guides/esp32-wifi)
- [Broker público de pruebas Mosquitto](https://test.mosquitto.org/)
- [MQTT.js](https://github.com/mqttjs/MQTT.js)
