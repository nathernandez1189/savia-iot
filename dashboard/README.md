# Tablero Savia IoT · Código fuente

React y Vite generan el [tablero público](https://nathernandez1189.github.io/savia-iot/). El navegador recibe telemetría por MQTT; la persistencia en AWS es una ruta separada.

## Ejecutar y comprobar

Requiere Node.js 22.13 o posterior. Desde `dashboard/`:

```bash
npm ci
npm run check
npm test
npm run dev
```

Para compilar: `npm run build`. Para revisar la compilación: `npm run preview`. Vite muestra la dirección local en la terminal.

## Publicación

[GitHub Actions](../.github/workflows/pages.yml) construye `dashboard/dist/` y lo publica en Pages al integrar cambios de `dashboard/` o los flujos en `main`. También se puede ejecutar **Publicar tablero → Run workflow**, seleccionando `main`. El flujo exige que pasen las pruebas de ambas prácticas y del tablero antes de publicar. GitHub Pages utiliza **Source: GitHub Actions**.

`dist/` y `node_modules/` se generan localmente y no se versionan. Las imágenes originales viven en `public/brand/` y se incorporan a la publicación durante la compilación. El enlace a Wokwi, el broker y el tópico están en [lib/protocol.ts](lib/protocol.ts); el dispositivo y el puente de la [Práctica 1](../practica-1/README.md) deben usar el mismo broker/tópico.

El 31 de octubre de 2026 se redujeron las dependencias declaradas de 45 a 14. La comprobación de tipos, las 12 pruebas y la compilación pasaron; antes de retirar las copias de la raíz se comprobó que HTML, CSS y JavaScript eran idénticos a la publicación anterior. Ese resultado verifica la compilación, no la llegada de nuevas lecturas del ESP32.

## Alcance

El historial se conserva por navegador. Open-Meteo aporta estimaciones exteriores y pronósticos; nunca sustituye lecturas del DHT22. El broker público es solo para la simulación. No se incluyen credenciales ni datos de un cultivo real.
