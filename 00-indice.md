# Índice y estado

Última actualización: **31 de octubre de 2026**.

| Entrega o componente | Estado acreditado | Dónde |
| --- | --- | --- |
| Práctica 1 | Implementada; pruebas locales y evidencias fechadas de Ubuntu/AWS | [practica-1/](practica-1/README.md) |
| Práctica 2 | Implementada; pruebas de colector y evidencias fechadas de MQTT/InfluxDB/Grafana | [practica2/](practica2/README.md) |
| Tablero público | Publicación desde el código mediante GitHub Actions; enlace actualizado a Wokwi | [dashboard/](dashboard/README.md) |
| Entregables | Archivos originales preservados en Releases | [Práctica 1](practica-1/entregables.md) · [Práctica 2](practica2/entregables/README.md) |
| Proyecto final | Estructura preparada; problema de IA y modelo pendientes | [proyecto-final/](proyecto-final/README.md) |

Este índice describe el repositorio. La calificación, la exposición y la entrega en CampusDigital se verifican en el curso; la reorganización no demuestra esos estados. Las evidencias históricas no garantizan que el laboratorio AWS siga activo.

## Siguientes pasos

- [ ] Confirmar los requisitos del proyecto final y definir una tarea de IA evaluable.
- [ ] Acordar el origen y etiquetado de los datos; conservar la distinción entre simulación, prueba sintética y medición física.
- [ ] Antes de una demostración, comprobar una lectura nueva con el mismo `boot` y `seq` en cada etapa.
- [ ] Decidir la licencia con el equipo. No se añadió una licencia por defecto.

## Verificación del código

La [acción Pruebas](https://github.com/nathernandez1189/savia-iot/actions/workflows/pruebas.yml) ejecuta 2 pruebas de la Práctica 1, 2 del colector de la Práctica 2 y 12 del tablero, además de comprobación de tipos y compilación. Las pruebas usan datos de prueba; no escriben en AWS ni validan una conexión activa de Wokwi.

Consulta [decisiones.md](decisiones.md) para la migración de carpetas y [AGENTS.md](AGENTS.md) para mantener este estado.
