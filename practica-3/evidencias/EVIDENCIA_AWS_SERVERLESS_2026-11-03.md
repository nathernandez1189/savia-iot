# Evidencia de Despliegue y Verificación — Práctica 3 (100% Serverless + IA en AWS)

- **Fecha:** 2026-11-03
- **Entorno:** AWS Academy Learner Lab (`us-east-1`, Cuenta `533267331933`, Rol `LabRole`)
- **Arquitectura:** ESP32 (mTLS X.509 puerto `8883`) $\rightarrow$ AWS IoT Core (`ESP32_Tomate_01`) $\rightarrow$ IoT Rule (`ReglaInvernaderoDynamo`) $\rightarrow$ Amazon DynamoDB (`telemetria_invernadero`) $\rightarrow$ AWS Lambda (`FetchTelemetria` + Motor IA) $\rightarrow$ Amazon API Gateway (`SaviaServerlessAPI`) $\rightarrow$ Amazon S3 Static Website Hosting.

---

## 1. Recursos Desplegados en AWS

| Servicio | Identificador / Endpoint Real | Estado |
| :--- | :--- | :--- |
| **AWS IoT Core Endpoint (ATS)** | `a1kk7h9pjd9qgn-ats.iot.us-east-1.amazonaws.com:8883` | Activo (TLS 1.2 + X.509) |
| **Thing / Política IoT** | `ESP32_Tomate_01` / `SaviaInvernaderoPolicy` | Activo |
| **IoT Rule SQL** | `ReglaInvernaderoDynamo` (`SELECT ... FROM 'invernadero1/telemetria'`) | Activa (`DynamoDBv2`) |
| **Tabla Amazon DynamoDB** | `telemetria_invernadero` (PK: `device_id`, SK: `timestamp`) | `ACTIVE` (`PAY_PER_REQUEST`) |
| **Función AWS Lambda** | `arn:aws:lambda:us-east-1:533267331933:function:FetchTelemetria` | `Active` (Python 3.12) |
| **Amazon API Gateway** | `https://kuls1pj325.execute-api.us-east-1.amazonaws.com` (`/sensor`, `/actuador`) | Activo (CORS `*`) |
| **Dashboard Público Amazon S3** | `http://savia-iot-serverless-533267331933-us-east-1.s3-website-us-east-1.amazonaws.com` | HTTP `200 OK` |

---

## 2. Prueba de Extremo a Extremo (End-to-End)

1. **Publicación MQTT sobre TLS 1.2 con Certificados X.509 (Puerto 8883):**
   - Tópico: `invernadero1/telemetria`
   - Resultado: `MQTT X.509 8883 Publish rc: 0`
2. **Inserción Automática por IoT Rule en DynamoDB:**
   - El conteo de registros en `telemetria_invernadero` subió de `6` a `7` en `< 2 s` sin intervención de servidores EC2.
3. **Inferencia del Motor de IA en AWS Lambda (`GET /sensor`):**
   - Acción IA: `VENTILACION_ACTIVA_CRITICA`
   - Diagnóstico: *"Estrés térmico activo (31.2 °C > 30 °C, VPD=1.88 kPa). Mantener ventilación encendida."*
4. **Control Remoto del Actuador (`POST /actuador`):**
   - Respuesta HTTP `200`: `{"ok": true, "published_mqtt": true, "topic": "invernadero1/actuador"}`
