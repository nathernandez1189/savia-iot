# Índice y estado

Última actualización: **3 de noviembre de 2026**.

| Entrega o componente | Estado acreditado | Dónde |
| --- | --- | --- |
| Práctica 1 | Implementada; pruebas locales y evidencias fechadas de Ubuntu/AWS | [practica-1/](practica-1/README.md) |
| Práctica 2 | Implementada; pruebas de colector y evidencias fechadas de MQTT/InfluxDB/Grafana | [Guía](practica2/README.md) · [Checklist](practica2/checklist-entrega.md) · [Evidencias](practica2/evidencias/README.md) |
| Práctica 3 | Implementada y verificada en AWS Serverless (IoT Core X.509, DynamoDB, Lambda IA, API Gateway y S3) con ESP32 físico | [Guía](practica-3/README.md) · [Evidencia AWS](practica-3/evidencias/EVIDENCIA_AWS_SERVERLESS_2026-11-03.md) |
| Tablero público | Publicación desde el código mediante GitHub Actions; enlace actualizado a Wokwi | [dashboard/](dashboard/README.md) |
| Entregables | Archivos originales preservados en Releases | [Práctica 1](practica-1/entregables.md) · [Práctica 2](practica2/entregables.md) |
| Proyecto final | Estructura preparada; motor de IA agronómica integrado en Práctica 3 | [proyecto-final/](proyecto-final/README.md) |

Este índice describe el repositorio. La calificación, la exposición y la entrega en CampusDigital se verifican en el curso. Las evidencias históricas acreditan sesiones fechadas de AWS Academy Learner Lab.

## Siguientes pasos

- [x] Implementar y verificar el flujo extremo a extremo de la Práctica 3 (ESP32 mTLS X.509 $\rightarrow$ IoT Core $\rightarrow$ DynamoDB $\rightarrow$ Lambda IA $\rightarrow$ API Gateway $\rightarrow$ S3).
- [ ] Sustentar la Práctica 3 en la sesión presencial del sábado.

## Verificación del código

La [acción Pruebas](https://github.com/nathernandez1189/savia-iot/actions/workflows/pruebas.yml) ejecuta 2 pruebas de la Práctica 1, 2 del colector de la Práctica 2, 5 de la función Lambda + Motor IA de la Práctica 3 y 12 del tablero, además de comprobación de tipos y compilación.

Consulta [decisiones.md](decisiones.md) para la bitácora técnica y [AGENTS.md](AGENTS.md) para mantener este estado.
