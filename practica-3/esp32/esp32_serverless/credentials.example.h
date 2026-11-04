/* Plantilla de credenciales y certificados X.509 para Práctica 3 (AWS IoT Core).
   INSTRUCCIONES:
   1. Copia este archivo como `credentials.h` en esta misma carpeta.
   2. El script `python practica-3/infra/deploy_serverless.py` genera `credentials.h`
      automáticamente al crear el Thing `ESP32_Tomate_01` en AWS IoT Core.
   3. NUNCA subas `credentials.h` a GitHub (ya está protegido en `.gitignore`).
*/

#ifndef SAVIA_CREDENTIALS_H
#define SAVIA_CREDENTIALS_H

#include <pgmspace.h>

const char WIFI_SSID[] = "CAMBIAR_POR_SSID_WIFI";
const char WIFI_PASSWORD[] = "CAMBIAR_POR_CLAVE_WIFI";

// Endpoint de datos ATS de AWS IoT Core (ej: xxxxxxxxxx-ats.iot.us-east-1.amazonaws.com)
const char AWS_IOT_ENDPOINT[] = "CAMBIAR_POR_ENDPOINT_IOT.iot.us-east-1.amazonaws.com";
const uint16_t AWS_IOT_PORT = 8883;

const char THING_NAME[] = "ESP32_Tomate_01";
const char DEVICE_ID[] = "esp32_invernadero_01";

// Amazon Root CA 1
static const char AWS_CERT_CA[] PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
REEMPLAZAR_CON_AMAZON_ROOT_CA_1
-----END CERTIFICATE-----
)EOF";

// Certificado del dispositivo (Device Certificate X.509)
static const char AWS_CERT_CRT[] PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
REEMPLAZAR_CON_CERTIFICADO_DEL_DISPOSITIVO
-----END CERTIFICATE-----
)EOF";

// Clave privada del dispositivo (Private Key)
static const char AWS_CERT_PRIVATE[] PROGMEM = R"EOF(
-----BEGIN RSA PRIVATE KEY-----
REEMPLAZAR_CON_CLAVE_PRIVADA_DEL_DISPOSITIVO
-----END RSA PRIVATE KEY-----
)EOF";

#endif
