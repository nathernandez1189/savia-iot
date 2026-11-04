"""AWS Lambda Serverless (`FetchTelemetria`) + Motor de IA Agronómica para Savia IoT.

Funciones:
1. GET /sensor: Consulta DynamoDB (`telemetria_invernadero`), ejecuta inferencia de IA
   agronómica (VPD, Punto de Rocío, Regresión Lineal +15/+30m, Riesgo de Botrytis,
   Detección de Anomalías Z-score) y responde JSON o CSV (`?format=csv`).
2. POST /actuador: Publica comandos remotos en AWS IoT Core (`invernadero1/actuador`)
   para controlar el ventilador/LED del ESP32 físico y registra el estado.
"""

from __future__ import annotations

import csv
import io
import json
import math
import os
import time
from decimal import Decimal
from typing import Any

try:
    import boto3
    from boto3.dynamodb.conditions import Key
except ImportError:  # Permite correr pruebas unitarias locales sin boto3 instalado
    boto3 = None  # type: ignore[assignment]
    Key = None  # type: ignore[assignment]

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "telemetria_invernadero")
DEFAULT_DEVICE_ID = os.environ.get("DEFAULT_DEVICE_ID", "esp32_invernadero_01")
COMMAND_TOPIC = os.environ.get("IOT_COMMAND_TOPIC", "invernadero1/actuador")
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Requested-With",
}


def _to_native(obj: Any) -> Any:
    """Convierte objetos Decimal de DynamoDB a float/int nativos para serialización JSON."""
    if isinstance(obj, list):
        return [_to_native(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _to_native(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else round(float(obj), 4)
    return obj


def compute_vpd_and_dew_point(temp_c: float, rh_pct: float) -> tuple[float, float]:
    """Calcula el Déficit de Presión de Vapor (VPD en kPa) y Punto de Rocío (°C)
    mediante la ecuación psicrométrica de Magnus-Tetens para Solanum lycopersicum.
    """
    rh_clamped = max(1.0, min(100.0, float(rh_pct)))
    temp_f = float(temp_c)
    # Presión de vapor de saturación (kPa)
    es = 0.61078 * math.exp((17.27 * temp_f) / (temp_f + 237.3))
    ea = es * (rh_clamped / 100.0)
    vpd = max(0.0, es - ea)

    # Punto de rocío (°C)
    alpha = ((17.27 * temp_f) / (237.3 + temp_f)) + math.log(rh_clamped / 100.0)
    dew_point = (237.3 * alpha) / (17.27 - alpha)
    return round(vpd, 2), round(dew_point, 1)


def _linear_forecast(timestamps_ms: list[int], values: list[float], horizon_minutes: float) -> tuple[float, float]:
    """Regresión lineal por mínimos cuadrados sobre serie temporal irregular.
    Retorna (valor_proyectado, pendiente_por_minuto).
    """
    n = len(values)
    if n == 0:
        return 0.0, 0.0
    if n == 1:
        return round(values[-1], 2), 0.0

    t0 = timestamps_ms[0]
    # Tiempo relativo en minutos; si los timestamps son muy cercanos (ej. cada 3s),
    # usamos paso mínimo efectivo para evitar extrapolaciones explosivas por ruido.
    span_min = (timestamps_ms[-1] - t0) / 60000.0
    if span_min < 0.25:
        xs = [i * (0.25 / max(1, n - 1)) for i in range(n)]
    else:
        xs = [(t - t0) / 60000.0 for t in timestamps_ms]

    mean_x = sum(xs) / n
    mean_y = sum(values) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, values))
    den = sum((x - mean_x) ** 2 for x in xs)
    slope = (num / den) if den > 1e-9 else 0.0
    # Acotar pendiente máxima plausible en invernadero (±0.8 °C/min o ±2.5 %HR/min)
    slope = max(-1.5, min(1.5, slope))
    projected = values[-1] + slope * horizon_minutes
    return round(projected, 2), round(slope, 3)


def analyze_agronomic_ai(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Ejecuta el motor de IA Agronómica sobre las lecturas cronológicas del invernadero."""
    if not records:
        return {
            "status": "SIN_DATOS",
            "vpd_kpa": None,
            "dew_point_c": None,
            "temp_pred_15m": None,
            "temp_pred_30m": None,
            "hum_pred_15m": None,
            "slope_temp_per_min": 0.0,
            "minutes_to_stress_30c": None,
            "botrytis_risk_pct": 0,
            "floral_stress_risk_pct": 0,
            "anomaly_detected": False,
            "anomaly_zscore": 0.0,
            "ai_action": "ESPERANDO_DATOS",
            "ai_diagnosis": "Sin lecturas disponibles en DynamoDB.",
        }

    window = records[-20:]
    temps = [float(r["temperatura"]) for r in window]
    hums = [float(r["humedad"]) for r in window]
    ts_list = [int(r["timestamp"]) for r in window]

    cur_temp = temps[-1]
    cur_hum = hums[-1]
    vpd_kpa, dew_point_c = compute_vpd_and_dew_point(cur_temp, cur_hum)

    temp_15m, slope_temp = _linear_forecast(ts_list, temps, 15.0)
    temp_30m, _ = _linear_forecast(ts_list, temps, 30.0)
    hum_15m, slope_hum = _linear_forecast(ts_list, hums, 15.0)
    hum_15m = max(0.0, min(100.0, hum_15m))

    # Estimación de tiempo hasta estrés térmico (>30 °C)
    minutes_to_stress = None
    if cur_temp >= 30.0:
        minutes_to_stress = 0.0
    elif slope_temp > 0.02:
        est = (30.0 - cur_temp) / slope_temp
        if est <= 120.0:
            minutes_to_stress = round(est, 1)

    # Clasificador probabilístico de riesgo de Botrytis cinerea (Moho Gris)
    dew_spread = cur_temp - dew_point_c
    botrytis_score = 0.0
    if cur_hum >= 75.0:
        botrytis_score += min(60.0, (cur_hum - 75.0) * 2.8)
    if dew_spread < 3.5:
        botrytis_score += min(30.0, (3.5 - dew_spread) * 10.0)
    if 15.0 <= cur_temp <= 26.0 and cur_hum >= 80.0:
        botrytis_score += 10.0
    botrytis_risk_pct = int(max(0.0, min(100.0, round(botrytis_score))))

    # Clasificador de riesgo de aborto floral / estrés térmico-hídrico
    floral_score = 0.0
    if cur_temp > 28.0:
        floral_score += min(65.0, (cur_temp - 28.0) * 16.0)
    if vpd_kpa > 1.5:
        floral_score += min(35.0, (vpd_kpa - 1.5) * 35.0)
    floral_stress_risk_pct = int(max(0.0, min(100.0, round(floral_score))))

    # Detección de anomalías mediante Z-score adaptativo sobre la ventana previa
    anomaly_detected = False
    z_score = 0.0
    if len(temps) >= 4:
        baseline = temps[:-1]
        mean_t = sum(baseline) / len(baseline)
        variance_t = sum((x - mean_t) ** 2 for x in baseline) / len(baseline)
        std_t = max(0.25, math.sqrt(variance_t))
        z_score = round(abs(cur_temp - mean_t) / std_t, 2)
        if z_score >= 2.2:
            anomaly_detected = True

    # Decisión y diagnóstico agronómico explicable
    if cur_temp > 30.0:
        ai_action = "VENTILACION_ACTIVA_CRITICA"
        ai_diagnosis = (
            f"Estrés térmico activo ({cur_temp:.1f} °C > 30 °C, VPD={vpd_kpa} kPa). "
            f"Riesgo de aborto floral del {floral_stress_risk_pct}%. Mantener ventilación encendida."
        )
    elif minutes_to_stress is not None and minutes_to_stress <= 15.0:
        ai_action = "PRE_ENFRIAMIENTO_IA"
        ai_diagnosis = (
            f"Alerta predictiva IA: Pendiente de +{slope_temp:.2f} °C/min cruzará 30 °C en ~{minutes_to_stress} min "
            f"(proyección +15m: {temp_15m:.1f} °C). Se recomienda pre-activar ventilación."
        )
    elif botrytis_risk_pct >= 60:
        ai_action = "DESHUMIDIFICAR_BOTRYTIS"
        ai_diagnosis = (
            f"Riesgo alto de Botrytis cinerea ({botrytis_risk_pct}%): HR={cur_hum:.1f}%, "
            f"punto de rocío a {dew_point_c:.1f} °C. Renovar aire para reducir humedad foliar."
        )
    else:
        ai_action = "CONFORT_AGRONOMICO"
        ai_diagnosis = (
            f"Microclima en rango óptimo para tomate (VPD={vpd_kpa} kPa, Rocío={dew_point_c:.1f} °C). "
            f"Proyección a +15 min estable en {temp_15m:.1f} °C."
        )

    return {
        "status": "ALERTA" if (cur_temp > 30.0 or botrytis_risk_pct >= 60 or anomaly_detected) else "OPTIMO",
        "vpd_kpa": vpd_kpa,
        "dew_point_c": dew_point_c,
        "temp_pred_15m": temp_15m,
        "temp_pred_30m": temp_30m,
        "hum_pred_15m": round(hum_15m, 1),
        "slope_temp_per_min": slope_temp,
        "slope_hum_per_min": slope_hum,
        "minutes_to_stress_30c": minutes_to_stress,
        "botrytis_risk_pct": botrytis_risk_pct,
        "floral_stress_risk_pct": floral_stress_risk_pct,
        "anomaly_detected": anomaly_detected,
        "anomaly_zscore": z_score,
        "ai_action": ai_action,
        "ai_diagnosis": ai_diagnosis,
    }


def records_to_csv(records: list[dict[str, Any]]) -> str:
    """Genera contenido CSV limpio para descarga desde el Dashboard S3."""
    fields = ["device_id", "timestamp", "temperatura", "humedad", "actuador_fan", "vpd_kpa", "riesgo_botrytis"]
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(fields)
    for r in records:
        vpd, _ = compute_vpd_and_dew_point(r.get("temperatura", 0.0), r.get("humedad", 0.0))
        writer.writerow([
            r.get("device_id", DEFAULT_DEVICE_ID),
            r.get("timestamp", 0),
            r.get("temperatura", 0.0),
            r.get("humedad", 0.0),
            bool(r.get("actuador_fan", False)),
            r.get("vpd_kpa", vpd),
            r.get("riesgo_botrytis", 0),
        ])
    return buf.getvalue()


def _normalize_record(item: dict[str, Any]) -> dict[str, Any]:
    """Normaliza nombres de campos tanto en español (directiva P3) como en inglés."""
    native = _to_native(item)
    temp = native.get("temperatura", native.get("temperature", 0.0))
    hum = native.get("humedad", native.get("humidity", 0.0))
    fan = bool(native.get("actuador_fan", native.get("fan", False)))
    ts = int(native.get("timestamp", native.get("ts", int(time.time() * 1000))))
    vpd, dew = compute_vpd_and_dew_point(temp, hum)
    return {
        "device_id": str(native.get("device_id", DEFAULT_DEVICE_ID)),
        "timestamp": ts,
        "temperatura": float(temp),
        "humedad": float(hum),
        "actuador_fan": fan,
        "modo": str(native.get("modo", native.get("mode", "AUTO"))),
        "vpd_kpa": float(native.get("vpd_kpa", vpd)),
        "dew_point_c": dew,
        "riesgo_botrytis": int(native.get("riesgo_botrytis", 0)),
    }


def fetch_records_from_dynamodb(device_id: str, limit: int = 50, table_resource: Any = None) -> list[dict[str, Any]]:
    """Consulta las últimas N lecturas en DynamoDB ordenadas cronológicamente."""
    if table_resource is None:
        if boto3 is None:
            raise RuntimeError("boto3 es requerido para conectar a DynamoDB")
        dynamodb = boto3.resource("dynamodb")
        table_resource = dynamodb.Table(TABLE_NAME)
        key_expr = Key("device_id").eq(device_id)
    else:
        key_expr = Key("device_id").eq(device_id) if Key is not None else device_id

    response = table_resource.query(
        KeyConditionExpression=key_expr,
        ScanIndexForward=False,
        Limit=max(1, min(200, int(limit))),
    )
    items = response.get("Items", [])
    normalized = [_normalize_record(i) for i in items]
    normalized.sort(key=lambda x: x["timestamp"])
    return normalized


def lambda_handler(event: dict[str, Any], context: Any = None, *, table_resource: Any = None, iot_client: Any = None) -> dict[str, Any]:
    """Punto de entrada principal para Amazon API Gateway (REST API v1 y HTTP API v2)."""
    method = (
        event.get("httpMethod")
        or event.get("requestContext", {}).get("http", {}).get("method")
        or "GET"
    ).upper()

    if method == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}

    params = event.get("queryStringParameters") or {}
    device_id = params.get("device_id", DEFAULT_DEVICE_ID)
    try:
        limit = int(params.get("limit", "50"))
    except (ValueError, TypeError):
        limit = 50

    if method == "POST":
        raw_body = event.get("body") or "{}"
        try:
            payload = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
                "body": json.dumps({"ok": False, "error": "JSON inválido"}),
            }

        fan_state = bool(payload.get("actuador_fan", False))
        modo = str(payload.get("modo", "MANUAL")).upper()
        if modo not in ("AUTO", "MANUAL"):
            modo = "MANUAL"

        command_msg = {
            "device_id": payload.get("device_id", device_id),
            "actuador_fan": fan_state,
            "modo": modo,
            "timestamp": int(time.time() * 1000),
        }

        published_mqtt = False
        mqtt_error = None
        try:
            if iot_client is None:
                iot_client = boto3.client("iot-data")
            iot_client.publish(
                topic=COMMAND_TOPIC,
                qos=1,
                payload=json.dumps(command_msg).encode("utf-8"),
            )
            published_mqtt = True
        except Exception as exc:
            mqtt_error = str(exc)

        return {
            "statusCode": 200,
            "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
            "body": json.dumps({
                "ok": True,
                "command": command_msg,
                "published_mqtt": published_mqtt,
                "topic": COMMAND_TOPIC,
                "note": mqtt_error,
            }),
        }

    # Flujo GET /sensor
    records = fetch_records_from_dynamodb(device_id=device_id, limit=limit, table_resource=table_resource)
    if params.get("format", "").lower() == "csv":
        csv_body = records_to_csv(records)
        return {
            "statusCode": 200,
            "headers": {
                **CORS_HEADERS,
                "Content-Type": "text/csv; charset=utf-8",
                "Content-Disposition": 'attachment; filename="telemetria_invernadero.csv"',
            },
            "body": csv_body,
        }

    ai_summary = analyze_agronomic_ai(records)
    latest = records[-1] if records else None
    return {
        "statusCode": 200,
        "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
        "body": json.dumps({
            "ok": True,
            "device_id": device_id,
            "count": len(records),
            "latest": latest,
            "ai": ai_summary,
            "records": records,
        }),
    }
