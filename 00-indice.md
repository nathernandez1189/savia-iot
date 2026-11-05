# Índice y estado

Última actualización documental: **5 de noviembre de 2026**.

| Entrega o componente | Estado acreditado | Dónde |
| --- | --- | --- |
| Práctica 1 | Implementada; pruebas locales y evidencias fechadas de Ubuntu/AWS | [practica-1/](practica-1/README.md) |
| Práctica 2 | Implementada; pruebas de colector y evidencias fechadas de MQTT/InfluxDB/Grafana | [Guía](practica2/README.md) · [Checklist](practica2/checklist-entrega.md) · [Evidencias](practica2/evidencias/README.md) |
| Práctica 3 | Código y servicios documentados; prueba MQTT con X.509 registrada en DynamoDB el 3 de noviembre. Origen físico del ESP32, descarga CSV y actuación remota aún sin evidencia completa | [Guía](practica-3/README.md) · [Checklist](practica-3/checklist-entrega.md) · [Evidencias](practica-3/evidencias/README.md) |
| Tablero público | Publicación desde el código mediante GitHub Actions; enlace actualizado a Wokwi | [dashboard/](dashboard/README.md) |
| Entregables | Prácticas 1 y 2 en Releases; Práctica 3 con índice de archivos y estado del informe | [Práctica 1](practica-1/entregables.md) · [Práctica 2](practica2/entregables.md) · [Práctica 3](practica-3/entregables.md) |
| Proyecto final | Estructura preparada; motor de IA agronómica integrado en Práctica 3 | [proyecto-final/](proyecto-final/README.md) |

Este índice describe el repositorio. La calificación, la exposición y la entrega en CampusDigital se verifican en el curso. Las evidencias históricas acreditan sesiones fechadas de AWS Academy Learner Lab.

## Siguientes pasos

- [x] Publicar código y verificar en una sesión una publicación MQTT con certificado X.509 que llega a DynamoDB.
- [ ] Documentar una lectura identificada desde el ESP32 hasta DynamoDB, el sitio S3 y el CSV.
- [ ] Documentar la recepción y ejecución de una orden remota en el ESP32.
- [ ] Sustentar la Práctica 3 frente al grupo y confirmar la entrega en el curso.

## Verificación del código

La [acción Pruebas](https://github.com/nathernandez1189/savia-iot/actions/workflows/pruebas.yml) ejecuta 2 pruebas de la Práctica 1, 2 del colector de la Práctica 2, 5 de la función Lambda + Motor IA de la Práctica 3 y 12 del tablero, además de comprobación de tipos y compilación.

Consulta [decisiones.md](decisiones.md) para la bitácora técnica y [AGENTS.md](AGENTS.md) para mantener este estado.
