# Tablero Savia IoT | Código fuente

Esta carpeta contiene la aplicación React y Vite publicada como [Savia IoT](https://nathernandez1189.github.io/savia-iot/). El sitio compilado se encuentra en la raíz del repositorio (`index.html`, `assets/`, `brand/`) para GitHub Pages. El tablero recibe telemetría del ESP32 simulado mediante MQTT en el navegador; el servidor AWS es una ruta de persistencia separada.

## Ejecutar y comprobar

Se requiere Node.js 22.13 o posterior. Desde esta carpeta:

```bash
npm ci
npm run check
npm test
npm run dev
```

La dirección local aparece en la terminal. Para compilar la publicación: `npm run build`. Los archivos quedan en `dashboard/dist/`, que no se sube a GitHub. Para actualizar GitHub Pages, copiar **el contenido** de `dashboard/dist/` a la raíz del repositorio y revisar los cambios antes de publicarlos.

El 24 de octubre de 2026 la comprobación de tipos y las 12 pruebas pasaron. Se compiló esta fuente y se compararon `dist/index.html`, el CSS y los dos módulos JavaScript con los archivos de la raíz: coincidieron byte por byte. Las imágenes de `public/brand/` también forman parte de la fuente.

## Alcance

El historial del tablero se conserva por navegador; no es una consulta a PostgreSQL. Open-Meteo aporta estimaciones **exteriores** y pronósticos; nunca sustituye lecturas del DHT22. El broker MQTT es público y se emplea solo con una simulación. No se incluyen credenciales ni datos de un cultivo real.
