"""Despliegue automatizado 100% Serverless en AWS Academy Learner Lab para Práctica 3.

Crea e integra de extremo a extremo:
1. Tabla Amazon DynamoDB: `telemetria_invernadero` (PK: `device_id`, SK: `timestamp`).
2. Objeto AWS IoT Core: `ESP32_Tomate_01`, política `SaviaInvernaderoPolicy`, certificados X.509
   y generación automática de `practica-3/esp32/esp32_serverless/credentials.h`.
3. Regla SQL de AWS IoT Core (`ReglaInvernaderoDynamo`) -> inserción directa en DynamoDB con `LabRole`.
4. Función AWS Lambda (`FetchTelemetria`, Python 3.12, `LabRole`) con Motor de IA Agronómica.
5. Amazon API Gateway (`SaviaServerlessAPI`) exponiendo `GET /sensor` y `POST /actuador` con CORS.
6. Bucket Amazon S3 con Static Website Hosting público sirviendo el Dashboard conectado a la API.
"""

from __future__ import annotations

import io
import json
import os
import time
import urllib.request
import zipfile
from decimal import Decimal
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

ROOT_DIR = Path(__file__).resolve().parent.parent
SECRETS_DIR = ROOT_DIR / ".secrets"
ESP32_DIR = ROOT_DIR / "esp32" / "esp32_serverless"
LAMBDA_FILE = ROOT_DIR / "lambda" / "lambda_function.py"
DASHBOARD_FILE = ROOT_DIR / "s3-dashboard" / "index.html"

REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
THING_NAME = "ESP32_Tomate_01"
DEVICE_ID = "esp32_invernadero_01"
POLICY_NAME = "SaviaInvernaderoPolicy"
RULE_NAME = "ReglaInvernaderoDynamo"
TABLE_NAME = "telemetria_invernadero"
LAMBDA_NAME = "FetchTelemetria"
API_NAME = "SaviaServerlessAPI"


def ensure_dynamodb_table(dynamodb_client, dynamodb_resource) -> None:
    print(f"[1/6] Verificando tabla DynamoDB `{TABLE_NAME}`...")
    try:
        dynamodb_client.describe_table(TableName=TABLE_NAME)
        print(f"      Tabla `{TABLE_NAME}` ya existe.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"      Creando tabla `{TABLE_NAME}` (PK=device_id, SK=timestamp)...")
            dynamodb_client.create_table(
                TableName=TABLE_NAME,
                KeySchema=[
                    {"AttributeName": "device_id", "KeyType": "HASH"},
                    {"AttributeName": "timestamp", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "device_id", "AttributeType": "S"},
                    {"AttributeName": "timestamp", "AttributeType": "N"},
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            waiter = dynamodb_client.get_waiter("table_exists")
            waiter.wait(TableName=TABLE_NAME)
            print(f"      Tabla `{TABLE_NAME}` activa.")
        else:
            raise

    # Sembrar datos iniciales si la tabla está vacía para que el Dashboard muestre curvas de inmediato
    table = dynamodb_resource.Table(TABLE_NAME)
    resp = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("device_id").eq(DEVICE_ID),
        Limit=1,
    )
    if not resp.get("Items"):
        print("      Insertando 6 lecturas semilla iniciales en DynamoDB...")
        now_ms = int(time.time() * 1000)
        seed_samples = [
            (now_ms - 25 * 60000, "26.8", "68.0", False, "1.12", 18),
            (now_ms - 20 * 60000, "27.4", "66.5", False, "1.22", 15),
            (now_ms - 15 * 60000, "28.1", "65.0", False, "1.33", 12),
            (now_ms - 10 * 60000, "28.9", "63.5", False, "1.45", 10),
            (now_ms - 5 * 60000,  "29.6", "62.0", False, "1.58", 8),
            (now_ms,              "30.4", "60.5", True,  "1.72", 5),
        ]
        for ts, t_str, h_str, fan, vpd_str, bot_risk in seed_samples:
            table.put_item(
                Item={
                    "device_id": DEVICE_ID,
                    "timestamp": ts,
                    "temperatura": Decimal(t_str),
                    "humedad": Decimal(h_str),
                    "actuador_fan": fan,
                    "modo": "AUTO",
                    "vpd_kpa": Decimal(vpd_str),
                    "riesgo_botrytis": bot_risk,
                }
            )


def ensure_iot_core_and_certs(iot_client, lab_role_arn: str, wifi_ssid: str, wifi_pass: str) -> str:
    print(f"[2/6] Configurando AWS IoT Core (`{THING_NAME}`) y certificados X.509...")
    endpoint = iot_client.describe_endpoint(endpointType="iot:Data-ATS")["endpointAddress"]
    iot_client.create_thing(thingName=THING_NAME)

    policy_doc = json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["iot:Connect", "iot:Publish", "iot:Subscribe", "iot:Receive"],
                "Resource": "*",
            }
        ],
    })
    try:
        iot_client.get_policy(policyName=POLICY_NAME)
    except ClientError:
        iot_client.create_policy(policyName=POLICY_NAME, policyDocument=policy_doc)

    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    cert_file = SECRETS_DIR / "device-certificate.pem.crt"
    key_file = SECRETS_DIR / "private.pem.key"
    ca_file = SECRETS_DIR / "AmazonRootCA1.pem"

    if not (cert_file.exists() and key_file.exists() and ca_file.exists()):
        print("      Generando nuevos certificados X.509 en AWS IoT Core...")
        cert_resp = iot_client.create_keys_and_certificate(setAsActive=True)
        cert_arn = cert_resp["certificateArn"]
        cert_pem = cert_resp["certificatePem"]
        key_pem = cert_resp["keyPair"]["PrivateKey"]

        with urllib.request.urlopen("https://www.amazontrust.com/repository/AmazonRootCA1.pem", timeout=10) as r:
            ca_pem = r.read().decode("utf-8")

        cert_file.write_text(cert_pem, encoding="utf-8")
        key_file.write_text(key_pem, encoding="utf-8")
        ca_file.write_text(ca_pem, encoding="utf-8")
        (SECRETS_DIR / "cert_arn.txt").write_text(cert_arn, encoding="utf-8")

        iot_client.attach_policy(policyName=POLICY_NAME, target=cert_arn)
        iot_client.attach_thing_principal(thingName=THING_NAME, principal=cert_arn)
    else:
        print("      Reutilizando certificados X.509 existentes en `practica-3/.secrets/`.")
        cert_pem = cert_file.read_text(encoding="utf-8")
        key_pem = key_file.read_text(encoding="utf-8")
        ca_pem = ca_file.read_text(encoding="utf-8")

    # Escribir credentials.h para el ESP32
    ESP32_DIR.mkdir(parents=True, exist_ok=True)
    creds_h = f"""// Generado automáticamente por deploy_serverless.py (protegido en .gitignore)
#ifndef SAVIA_CREDENTIALS_H
#define SAVIA_CREDENTIALS_H

#include <pgmspace.h>

const char WIFI_SSID[] = "{wifi_ssid}";
const char WIFI_PASSWORD[] = "{wifi_pass}";

const char AWS_IOT_ENDPOINT[] = "{endpoint}";
const uint16_t AWS_IOT_PORT = 8883;

const char THING_NAME[] = "{THING_NAME}";
const char DEVICE_ID[] = "{DEVICE_ID}";

static const char AWS_CERT_CA[] PROGMEM = R"EOF(
{ca_pem.strip()}
)EOF";

static const char AWS_CERT_CRT[] PROGMEM = R"EOF(
{cert_pem.strip()}
)EOF";

static const char AWS_CERT_PRIVATE[] PROGMEM = R"EOF(
{key_pem.strip()}
)EOF";

#endif
"""
    (ESP32_DIR / "credentials.h").write_text(creds_h, encoding="utf-8")
    print(f"      Archivo `{ESP32_DIR / 'credentials.h'}` generado y listo para Arduino IDE.")

    # Configurar IoT Rule -> DynamoDBv2
    print(f"[3/6] Configurando IoT Rule `{RULE_NAME}` -> DynamoDB `{TABLE_NAME}`...")
    rule_payload = {
        "sql": "SELECT device_id, timestamp() AS timestamp, temperatura, humedad, actuador_fan, modo, vpd_kpa, riesgo_botrytis FROM 'invernadero1/telemetria'",
        "description": "Enrutamiento directo Serverless de Savia IoT hacia DynamoDB",
        "actions": [
            {
                "dynamoDBv2": {
                    "roleArn": lab_role_arn,
                    "putItem": {"tableName": TABLE_NAME},
                }
            }
        ],
        "ruleDisabled": False,
        "awsIotSqlVersion": "2016-03-23",
    }
    try:
        iot_client.get_topic_rule(ruleName=RULE_NAME)
        iot_client.replace_topic_rule(ruleName=RULE_NAME, topicRulePayload=rule_payload)
    except ClientError:
        iot_client.create_topic_rule(ruleName=RULE_NAME, topicRulePayload=rule_payload)

    return endpoint


def ensure_lambda_function(lambda_client, lab_role_arn: str) -> str:
    print(f"[4/6] Empaquetando y desplegando función AWS Lambda `{LAMBDA_NAME}`...")
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(LAMBDA_FILE, arcname="lambda_function.py")
    zip_bytes = zip_buffer.getvalue()

    env_vars = {
        "Variables": {
            "DYNAMODB_TABLE": TABLE_NAME,
            "DEFAULT_DEVICE_ID": DEVICE_ID,
            "IOT_COMMAND_TOPIC": "invernadero1/actuador",
        }
    }

    try:
        lambda_client.get_function(FunctionName=LAMBDA_NAME)
        lambda_client.update_function_code(FunctionName=LAMBDA_NAME, ZipFile=zip_bytes)
        waiter = lambda_client.get_waiter("function_updated")
        waiter.wait(FunctionName=LAMBDA_NAME)
        resp = lambda_client.update_function_configuration(
            FunctionName=LAMBDA_NAME,
            Role=lab_role_arn,
            Handler="lambda_function.lambda_handler",
            Runtime="python3.12",
            Timeout=15,
            Environment=env_vars,
        )
        fn_arn = resp["FunctionArn"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            resp = lambda_client.create_function(
                FunctionName=LAMBDA_NAME,
                Runtime="python3.12",
                Role=lab_role_arn,
                Handler="lambda_function.lambda_handler",
                Code={"ZipFile": zip_bytes},
                Timeout=15,
                MemorySize=256,
                Environment=env_vars,
            )
            fn_arn = resp["FunctionArn"]
            waiter = lambda_client.get_waiter("function_active_v2")
            waiter.wait(FunctionName=LAMBDA_NAME)
        else:
            raise

    print(f"      Lambda activa: {fn_arn}")
    return fn_arn


def ensure_api_gateway(apigw_client, lambda_client, lambda_arn: str, account_id: str) -> str:
    print(f"[5/6] Configurando Amazon API Gateway `{API_NAME}` (`/sensor` y `/actuador`)...")
    apis = apigw_client.get_apis().get("Items", [])
    existing = next((a for a in apis if a["Name"] == API_NAME), None)

    cors_config = {
        "AllowOrigins": ["*"],
        "AllowMethods": ["GET", "POST", "OPTIONS"],
        "AllowHeaders": ["Content-Type", "Authorization", "X-Requested-With"],
    }

    if existing:
        api_id = existing["ApiId"]
        api_endpoint = existing["ApiEndpoint"]
        apigw_client.update_api(ApiId=api_id, CorsConfiguration=cors_config)
    else:
        created = apigw_client.create_api(
            Name=API_NAME,
            ProtocolType="HTTP",
            CorsConfiguration=cors_config,
        )
        api_id = created["ApiId"]
        api_endpoint = created["ApiEndpoint"]

    integ = apigw_client.create_integration(
        ApiId=api_id,
        IntegrationType="AWS_PROXY",
        IntegrationUri=lambda_arn,
        PayloadFormatVersion="2.0",
    )
    integ_id = integ["IntegrationId"]

    existing_routes = {r["RouteKey"] for r in apigw_client.get_routes(ApiId=api_id).get("Items", [])}
    for route_key in ("GET /sensor", "POST /actuador", "$default"):
        if route_key not in existing_routes:
            apigw_client.create_route(
                ApiId=api_id,
                RouteKey=route_key,
                Target=f"integrations/{integ_id}",
            )

    stages = {s["StageName"] for s in apigw_client.get_stages(ApiId=api_id).get("Items", [])}
    if "$default" not in stages:
        apigw_client.create_stage(ApiId=api_id, StageName="$default", AutoDeploy=True)

    try:
        lambda_client.add_permission(
            FunctionName=LAMBDA_NAME,
            StatementId=f"AllowAPIGatewayInvoke-{api_id}",
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=f"arn:aws:execute-api:{REGION}:{account_id}:{api_id}/*/*",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceConflictException":
            raise

    print(f"      API Gateway URL: {api_endpoint}")
    return api_endpoint


def ensure_s3_dashboard(s3_client, account_id: str, api_endpoint: str) -> str:
    bucket_name = f"savia-iot-serverless-{account_id}-{REGION}"
    print(f"[6/6] Configurando Bucket Amazon S3 Static Website `{bucket_name}`...")

    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        if REGION == "us-east-1":
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": REGION},
            )

    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": False,
            "IgnorePublicAcls": False,
            "BlockPublicPolicy": False,
            "RestrictPublicBuckets": False,
        },
    )

    bucket_policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
            }
        ],
    })
    s3_client.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)

    s3_client.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration={
            "IndexDocument": {"Suffix": "index.html"},
        },
    )

    html_raw = DASHBOARD_FILE.read_text(encoding="utf-8")
    html_configured = html_raw.replace("__API_GATEWAY_URL__", api_endpoint)
    s3_client.put_object(
        Bucket=bucket_name,
        Key="index.html",
        Body=html_configured.encode("utf-8"),
        ContentType="text/html; charset=utf-8",
        CacheControl="no-cache",
    )

    brand_icon = ROOT_DIR.parent / "dashboard" / "public" / "brand" / "savia-symbol.png"
    if brand_icon.exists():
        s3_client.put_object(
            Bucket=bucket_name,
            Key="brand/savia-symbol.png",
            Body=brand_icon.read_bytes(),
            ContentType="image/png",
            CacheControl="max-age=86400",
        )

    s3_url = f"http://{bucket_name}.s3-website-{REGION}.amazonaws.com"
    print(f"      Dashboard S3 publicado en: {s3_url}")
    return s3_url


def main() -> None:
    session = boto3.Session(region_name=REGION)
    sts = session.client("sts")
    identity = sts.get_caller_identity()
    account_id = identity["Account"]
    lab_role_arn = f"arn:aws:iam::{account_id}:role/LabRole"

    print("==================================================================")
    print(f"Desplegando Savia IoT Práctica 3 (Serverless) en Cuenta {account_id}")
    print(f"Rol IAM (Learner Lab): {lab_role_arn}")
    print("==================================================================")

    wifi_ssid = os.environ.get("SAVIA_WIFI_SSID", "CAMBIAR_POR_TU_SSID_WIFI")
    wifi_pass = os.environ.get("SAVIA_WIFI_PASS", "CAMBIAR_POR_TU_CLAVE_WIFI")

    dynamodb_client = session.client("dynamodb")
    dynamodb_resource = session.resource("dynamodb")
    iot_client = session.client("iot")
    lambda_client = session.client("lambda")
    apigw_client = session.client("apigatewayv2")
    s3_client = session.client("s3")

    ensure_dynamodb_table(dynamodb_client, dynamodb_resource)
    iot_endpoint = ensure_iot_core_and_certs(iot_client, lab_role_arn, wifi_ssid, wifi_pass)
    lambda_arn = ensure_lambda_function(lambda_client, lab_role_arn)
    api_endpoint = ensure_api_gateway(apigw_client, lambda_client, lambda_arn, account_id)
    s3_url = ensure_s3_dashboard(s3_client, account_id, api_endpoint)

    summary = {
        "account_id": account_id,
        "region": REGION,
        "iot_endpoint": iot_endpoint,
        "thing_name": THING_NAME,
        "dynamodb_table": TABLE_NAME,
        "lambda_function": LAMBDA_NAME,
        "api_gateway_url": api_endpoint,
        "s3_dashboard_url": s3_url,
    }
    out_file = ROOT_DIR / "infra" / "deployed_endpoints.json"
    out_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\n==================================================================")
    print("DESPLIEGUE SERVERLESS COMPLETADO CON ÉXITO")
    print("==================================================================")
    print(f"1. AWS IoT Core Endpoint (8883): {iot_endpoint}")
    print(f"2. Tabla DynamoDB:               {TABLE_NAME}")
    print(f"3. API Gateway GET /sensor:      {api_endpoint}/sensor")
    print(f"4. API Gateway POST /actuador:   {api_endpoint}/actuador")
    print(f"5. Dashboard Público Amazon S3:  {s3_url}")
    print(f"6. Credenciales ESP32 listas en: {ESP32_DIR / 'credentials.h'}")
    print("==================================================================")


if __name__ == "__main__":
    main()
