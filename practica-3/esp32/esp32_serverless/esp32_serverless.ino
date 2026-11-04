/* Savia IoT - Práctica 3: Arquitectura 100% Serverless + Edge AI (ESP32)
   - Ingesta segura MQTT sobre TLS 1.2 (Puerto 8883) con certificados X.509 en AWS IoT Core.
   - Publica telemetría + inferencia Edge (VPD y riesgo de Botrytis) en `invernadero1/telemetria`.
   - Recibe comandos remotos desde el Dashboard S3 / API Gateway / Lambda en `invernadero1/actuador`.
*/

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHTesp.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <time.h>
#include <math.h>

#if __has_include("credentials.h")
  #include "credentials.h"
#else
  #include "credentials.example.h"
#endif

// --- PINES HARDWARE ---
const uint8_t PIN_DHT = 15;
const uint8_t PIN_RELE = 26;
const uint8_t PIN_ALERTA = 27;
const uint8_t PIN_AUTO = 18;
const uint8_t PIN_ON = 19;
const uint8_t PIN_OFF = 23;

// --- TÓPICOS MQTT EN AWS IOT CORE ---
const char* TOPIC_TELEMETRY = "invernadero1/telemetria";
const char* TOPIC_ACTUATOR  = "invernadero1/actuador";

// --- OBJETOS ---
DHTesp dht;
LiquidCrystal_I2C lcd(0x27, 20, 4);
WiFiClientSecure netSecure;
PubSubClient mqtt(netSecure);

bool automatico = true;
bool actuador_fan = false;
bool sensorValido = false;
float temperatura = 0.0;
float humedad = 0.0;
float vpd_kpa = 0.0;
int riesgo_botrytis = 0;

unsigned long lastSample = 0;
unsigned long lastConnect = 0;
unsigned long lastWifiAttempt = 0;
uint32_t seq = 0;

struct Boton {
  uint8_t pin;
  bool prev = HIGH;
  bool stable = HIGH;
  unsigned long changed = 0;
};
Boton bAuto{PIN_AUTO}, bOn{PIN_ON}, bOff{PIN_OFF};

bool pushed(Boton &b) {
  bool x = digitalRead(b.pin);
  if (x != b.prev) { b.changed = millis(); b.prev = x; }
  if (millis() - b.changed >= 30 && x != b.stable) {
    b.stable = x;
    return x == LOW;
  }
  return false;
}

// --- INFERENCIA LIGERA EN EL BORDE (EDGE AI) ---
void computeEdgeAI(float t, float hr) {
  float rh = hr < 1.0f ? 1.0f : (hr > 100.0f ? 100.0f : hr);
  float es = 0.61078f * expf((17.27f * t) / (t + 237.3f));
  float ea = es * (rh / 100.0f);
  vpd_kpa = es - ea;
  if (vpd_kpa < 0.0f) vpd_kpa = 0.0f;

  float alpha = ((17.27f * t) / (237.3f + t)) + logf(rh / 100.0f);
  float dew = (237.3f * alpha) / (17.27f - alpha);
  float spread = t - dew;

  float score = 0.0f;
  if (rh >= 75.0f) score += fminf(60.0f, (rh - 75.0f) * 2.8f);
  if (spread < 3.5f) score += fminf(30.0f, (3.5f - spread) * 10.0f);
  if (t >= 15.0f && t <= 26.0f && rh >= 80.0f) score += 10.0f;
  riesgo_botrytis = (int)fmaxf(0.0f, fminf(100.0f, roundf(score)));
}

void line(uint8_t row, String s) {
  lcd.setCursor(0, row);
  s = s.substring(0, 20);
  while (s.length() < 20) s += ' ';
  lcd.print(s);
}

void control() {
  if (!sensorValido) {
    actuador_fan = false;
    return;
  }
  if (automatico) {
    if (temperatura > 30.0f) actuador_fan = true;
    else if (temperatura < 27.0f) actuador_fan = false;
  }
}

void outputs() {
  digitalWrite(PIN_RELE, actuador_fan ? HIGH : LOW);
  digitalWrite(PIN_ALERTA, (!sensorValido || temperatura > 30.0f || riesgo_botrytis >= 60) ? HIGH : LOW);

  line(0, sensorValido ? "T:" + String(temperatura, 1) + "C HR:" + String(humedad, 0) + "%" : "DHT22 SIN LECTURA");
  line(1, sensorValido ? "VPD:" + String(vpd_kpa, 2) + "kPa R:" + String(riesgo_botrytis) + "%" : "Revisar sensor");
  line(2, String(automatico ? "AUTO" : "MANUAL") + " | VENT " + (actuador_fan ? "ON" : "OFF"));
  line(3, String(mqtt.connected() ? "IOT TLS OK" : "LOCAL MODO"));
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  if (length > 512) return;
  JsonDocument doc;
  if (deserializeJson(doc, payload, length)) return;

  if (doc["modo"].is<const char*>()) {
    String m = doc["modo"].as<String>();
    m.toUpperCase();
    automatico = (m == "AUTO");
  } else {
    automatico = false;
  }

  if (doc["actuador_fan"].is<bool>()) {
    actuador_fan = doc["actuador_fan"].as<bool>();
  }

  control();
  outputs();
  lastSample = 0; // Publica el nuevo estado a DynamoDB de inmediato
  Serial.printf(">>> Comando remoto AWS recibido: modo=%s | actuador_fan=%s\n",
                automatico ? "AUTO" : "MANUAL", actuador_fan ? "ON" : "OFF");
}

void connectAWSIoT() {
  if (WiFi.status() != WL_CONNECTED) return;
  if (mqtt.connected() || millis() - lastConnect < 5000) return;
  lastConnect = millis();

  Serial.print("Conectando a AWS IoT Core (mTLS X.509 8883)... ");
  if (mqtt.connect(THING_NAME)) {
    Serial.println("CONECTADO!");
    mqtt.subscribe(TOPIC_ACTUATOR);
    outputs();
  } else {
    Serial.printf("Fallo rc=%d\n", mqtt.state());
  }
}

uint64_t currentTimestampMs() {
  time_t now = time(nullptr);
  if (now > 1700000000) {
    return (uint64_t)now * 1000ULL + (millis() % 1000ULL);
  }
  return (uint64_t)millis();
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_RELE, OUTPUT);
  pinMode(PIN_ALERTA, OUTPUT);
  pinMode(PIN_AUTO, INPUT_PULLUP);
  pinMode(PIN_ON, INPUT_PULLUP);
  pinMode(PIN_OFF, INPUT_PULLUP);

  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();
  dht.setup(PIN_DHT, DHTesp::DHT22);

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");

  // Configurar certificados X.509 en WiFiClientSecure
  netSecure.setCACert(AWS_CERT_CA);
  netSecure.setCertificate(AWS_CERT_CRT);
  netSecure.setPrivateKey(AWS_CERT_PRIVATE);

  mqtt.setServer(AWS_IOT_ENDPOINT, AWS_IOT_PORT);
  mqtt.setBufferSize(1024);
  mqtt.setKeepAlive(30);
  mqtt.setCallback(onMqttMessage);

  outputs();
  Serial.println("Savia IoT - Practica 3 Serverless (AWS IoT Core X.509 + DynamoDB + Lambda IA + S3)");
}

void loop() {
  if (pushed(bAuto)) { automatico = true; control(); outputs(); }
  if (pushed(bOn))   { automatico = false; actuador_fan = sensorValido; control(); outputs(); }
  if (pushed(bOff))  { automatico = false; actuador_fan = false; control(); outputs(); }

  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'a' || c == 'A') { automatico = true; control(); outputs(); Serial.println(">>> Modo AUTO activado por Serial"); }
    else if (c == '1') { automatico = false; actuador_fan = sensorValido; control(); outputs(); Serial.println(">>> Ventilador ON (MANUAL) por Serial"); }
    else if (c == '0') { automatico = false; actuador_fan = false; control(); outputs(); Serial.println(">>> Ventilador OFF (MANUAL) por Serial"); }
  }

  if (WiFi.status() != WL_CONNECTED && millis() - lastWifiAttempt >= 5000) {
    lastWifiAttempt = millis();
    WiFi.reconnect();
  }

  connectAWSIoT();
  if (mqtt.connected()) mqtt.loop();

  if (millis() - lastSample >= 4000) {
    lastSample = millis();
    TempAndHumidity r = dht.getTempAndHumidity();
    sensorValido = !isnan(r.temperature) && !isnan(r.humidity) &&
                   r.temperature >= -40.0f && r.temperature <= 80.0f &&
                   r.humidity >= 0.0f && r.humidity <= 100.0f;

    if (sensorValido) {
      temperatura = r.temperature;
      humedad = r.humidity;
      computeEdgeAI(temperatura, humedad);
    }

    control();
    outputs();

    if (sensorValido && mqtt.connected()) {
      JsonDocument doc;
      doc["device_id"] = DEVICE_ID;
      doc["timestamp"] = currentTimestampMs();
      doc["temperatura"] = roundf(temperatura * 10.0f) / 10.0f;
      doc["humedad"] = roundf(humedad * 10.0f) / 10.0f;
      doc["actuador_fan"] = actuador_fan;
      doc["modo"] = automatico ? "AUTO" : "MANUAL";
      doc["vpd_kpa"] = roundf(vpd_kpa * 100.0f) / 100.0f;
      doc["riesgo_botrytis"] = riesgo_botrytis;
      doc["seq"] = ++seq;

      String payload;
      serializeJson(doc, payload);
      bool ok = mqtt.publish(TOPIC_TELEMETRY, payload.c_str(), false);
      Serial.printf("IoT Core #%lu [%s]: %s\n", (unsigned long)seq, ok ? "OK" : "ERR", payload.c_str());
    }
  }

  delay(10);
}
