/* Savia IoT - Práctica 2. ESP32 y DHT22 simulados.
   Antes de ejecutar, configurar la IP/host de AWS y credenciales TEMPORALES
   del usuario savia_device. No publicar una copia con claves reales.
   El proyecto original de la Práctica 1 permanece intacto.
*/
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHTesp.h>
#include <time.h>

const char* MQTT_HOST = "CAMBIAR_POR_IP_O_HOST_AWS";
const uint16_t MQTT_PORT = 1883;
const char* MQTT_USER = "savia_device";
const char* MQTT_PASSWORD = "CAMBIAR_POR_CLAVE_TEMPORAL";
const char* TOPIC_DATA = "invernadero1/telemetria";
const char* TOPIC_TEMP = "invernadero1/temperatura";
const char* TOPIC_HUM = "invernadero1/humedad";
const uint8_t PIN_DHT = 15, PIN_LED = 26;

WiFiClient network;
PubSubClient mqtt(network);
DHTesp dht;
char boot[9];
uint32_t seq = 0;
bool fan = false;
unsigned long lastSample = 0, lastConnect = 0, lastWifiAttempt = 0;

void reconnect() {
  if (WiFi.status() != WL_CONNECTED) return;
  if (mqtt.connected() || millis() - lastConnect < 5000) return;
  lastConnect = millis();
  String id = String("savia-p2-") + boot;
  if (mqtt.connect(id.c_str(), MQTT_USER, MQTT_PASSWORD)) {
    Serial.println("MQTT AWS autenticado");
  } else {
    Serial.printf("MQTT desconectado, estado %d\n", mqtt.state());
  }
}

void setup() {
  Serial.begin(115200);
  snprintf(boot, sizeof(boot), "%08lx", (unsigned long)esp_random());
  pinMode(PIN_LED, OUTPUT);
  dht.setup(PIN_DHT, DHTesp::DHT22);
  WiFi.mode(WIFI_STA);
  WiFi.begin("Wokwi-GUEST", "", 6);
  configTime(0, 0, "pool.ntp.org");
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(1024);
  mqtt.setKeepAlive(20);
  Serial.println("Savia IoT Practica 2: DHT22 → AWS MQTT → InfluxDB/CSV → Grafana");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED && millis() - lastWifiAttempt >= 5000) {
    lastWifiAttempt = millis();
    WiFi.reconnect();
  }
  reconnect();
  if (mqtt.connected()) mqtt.loop();
  if (millis() - lastSample >= 5000) {
    lastSample = millis();
    TempAndHumidity reading = dht.getTempAndHumidity();
    if (isnan(reading.temperature) || isnan(reading.humidity)) {
      Serial.println("DHT22 sin lectura; no se envian valores inventados");
      return;
    }
    if (reading.temperature > 30) fan = true;
    else if (reading.temperature < 27) fan = false;
    digitalWrite(PIN_LED, fan ? HIGH : LOW);
    if (!mqtt.connected()) {
      Serial.println("Control local activo; sin enlace MQTT");
      return;
    }
    JsonDocument doc;
    doc["v"] = 2;
    doc["boot"] = boot;
    doc["seq"] = ++seq;
    doc["temperature"] = reading.temperature;
    doc["humidity"] = reading.humidity;
    doc["mode"] = "AUTO";
    doc["fan"] = fan;
    doc["alarm"] = reading.humidity < 50 ? "BAJA" : reading.humidity > 85 ? "ALTA" : "NORMAL";
    doc["reason"] = "lectura";
    String json;
    serializeJson(doc, json);
    bool ok = mqtt.publish(TOPIC_DATA, json.c_str(), false);
    String temp = String(reading.temperature, 1), hum = String(reading.humidity, 1);
    mqtt.publish(TOPIC_TEMP, temp.c_str(), false);
    mqtt.publish(TOPIC_HUM, hum.c_str(), false);
    Serial.printf("%s #%lu: T=%.1f C, HR=%.1f%%, vent=%s\n",
                  ok ? "Enviado" : "Error", (unsigned long)seq,
                  reading.temperature, reading.humidity, fan ? "ON" : "OFF");
  }
  delay(10);
}
