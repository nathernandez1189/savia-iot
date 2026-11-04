/* Savia IoT - Práctica 2 (Hardware Físico ESP32)
   Conexión a Broker MQTT Mosquitto en AWS EC2 (IP Elástica).
   Persistencia en SQLite Outbox -> InfluxDB OSS 2.x -> Grafana 11.5.
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHTesp.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <time.h>

// --- CONFIGURACIÓN DE PINES ---
const uint8_t PIN_DHT = 15;
const uint8_t PIN_RELE = 26;
const uint8_t PIN_ALERTA = 27;
const uint8_t PIN_AUTO = 18;
const uint8_t PIN_ON = 19;
const uint8_t PIN_OFF = 23;

// --- CONFIGURACIÓN RED Y AWS ---
const char* WIFI_SSID = "CAMBIAR_POR_SSID";
const char* WIFI_PASS = "CAMBIAR_POR_CLAVE_WIFI";

const char* MQTT_HOST = "CAMBIAR_POR_IP_O_HOST_AWS";
const uint16_t MQTT_PORT = 1883;
const char* MQTT_USER = "savia_device";
const char* MQTT_PASSWORD = "CAMBIAR_POR_CLAVE_TEMPORAL";

const char* TOPIC_DATA = "invernadero1/telemetria";
const char* TOPIC_TEMP = "invernadero1/temperatura";
const char* TOPIC_HUM  = "invernadero1/humedad";

// --- OBJETOS Y VARIABLES ---
DHTesp dht;
LiquidCrystal_I2C lcd(0x27, 20, 4);
WiFiClient network;
PubSubClient mqtt(network);

char boot[9];
uint32_t seq = 0;
bool automatico = true;
bool ventilador = false;
bool sensorValido = false;
float temperatura = 0.0;
float humedad = 0.0;
unsigned long lastSample = 0;
unsigned long lastConnect = 0;
unsigned long lastWifiAttempt = 0;

// --- ESTRUCTURA BOTÓN ANTIRREBOTE ---
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

uint8_t alarmCode() {
  if (!sensorValido) return 3;
  if (humedad < 50) return 1;
  if (humedad > 85) return 2;
  return 0;
}

const char* alarmText(uint8_t code) {
  if (code == 3) return "SENSOR";
  if (code == 1) return "BAJA";
  if (code == 2) return "ALTA";
  return "NORMAL";
}

void line(uint8_t row, String s) {
  lcd.setCursor(0, row);
  s = s.substring(0, 20);
  while (s.length() < 20) s += ' ';
  lcd.print(s);
}

void control() {
  if (!sensorValido) {
    ventilador = false;
    return;
  }
  if (automatico) {
    if (temperatura > 30.0) ventilador = true;
    else if (temperatura < 27.0) ventilador = false;
  }
}

void outputs() {
  digitalWrite(PIN_RELE, ventilador ? HIGH : LOW);
  digitalWrite(PIN_ALERTA, alarmCode() != 0);

  line(0, sensorValido ? "Temp: " + String(temperatura, 1) + " C" : "DHT22 SIN LECTURA");
  line(1, sensorValido ? "Humedad: " + String(humedad, 1) + " %" : "Revisar sensor");
  line(2, String(automatico ? "AUTO" : "MANUAL") + " | VENT " + (ventilador ? "ON" : "OFF"));
  line(3, String(mqtt.connected() ? "AWS OK | " : "AWS LOCAL | ") + alarmText(alarmCode()));
}

void reconnect() {
  if (WiFi.status() != WL_CONNECTED) return;
  if (mqtt.connected() || millis() - lastConnect < 5000) return;
  lastConnect = millis();

  String id = String("savia-hw-") + boot;
  if (mqtt.connect(id.c_str(), MQTT_USER, MQTT_PASSWORD)) {
    Serial.println(">>> MQTT AWS Autenticado con éxito (Mosquitto 1883)");
    outputs();
  } else {
    Serial.printf(">>> MQTT AWS Desconectado, rc=%d\n", mqtt.state());
  }
}

void setup() {
  Serial.begin(115200);
  snprintf(boot, sizeof(boot), "%08lx", (unsigned long)esp_random());

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
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  configTime(0, 0, "pool.ntp.org");

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(1024);
  mqtt.setKeepAlive(20);

  Serial.println("==================================================");
  Serial.println("Savia IoT - Práctica 2: ESP32 Físico -> AWS Cloud");
  Serial.printf("Broker: %s:%d | Boot ID: %s\n", MQTT_HOST, MQTT_PORT, boot);
  Serial.println("==================================================");

  outputs();
}

void loop() {
  // Manejo de botones físicos
  if (pushed(bAuto)) { automatico = true; control(); outputs(); }
  if (pushed(bOn))   { automatico = false; ventilador = sensorValido; control(); outputs(); }
  if (pushed(bOff))  { automatico = false; ventilador = false; control(); outputs(); }

  // Reconexión Wi-Fi
  if (WiFi.status() != WL_CONNECTED && millis() - lastWifiAttempt >= 5000) {
    lastWifiAttempt = millis();
    WiFi.reconnect();
  }

  // Reconexión MQTT
  reconnect();
  if (mqtt.connected()) mqtt.loop();

  // Muestreo cada 2.5 segundos
  if (millis() - lastSample >= 2500) {
    lastSample = millis();
    TempAndHumidity reading = dht.getTempAndHumidity();
    sensorValido = !isnan(reading.temperature) && !isnan(reading.humidity) &&
                   reading.temperature >= -40 && reading.temperature <= 80 &&
                   reading.humidity >= 0 && reading.humidity <= 100;

    if (sensorValido) {
      temperatura = reading.temperature;
      humedad = reading.humidity;
    }

    control();
    outputs();

    if (sensorValido && mqtt.connected()) {
      JsonDocument doc;
      doc["v"] = 2;
      doc["boot"] = boot;
      doc["seq"] = ++seq;
      doc["temperature"] = temperatura;
      doc["humidity"] = humedad;
      doc["mode"] = automatico ? "AUTO" : "MANUAL";
      doc["fan"] = ventilador;
      doc["alarm"] = alarmText(alarmCode());
      doc["reason"] = "lectura";

      String json;
      serializeJson(doc, json);

      bool ok = mqtt.publish(TOPIC_DATA, json.c_str(), false);
      String sTemp = String(temperatura, 1);
      String sHum = String(humedad, 1);
      mqtt.publish(TOPIC_TEMP, sTemp.c_str(), false);
      mqtt.publish(TOPIC_HUM, sHum.c_str(), false);

      Serial.printf("AWS #%lu: T=%.1f C | HR=%.1f %% | %s | Vent=%s | %s\n",
                    (unsigned long)seq, temperatura, humedad,
                    automatico ? "AUTO" : "MANUAL",
                    ventilador ? "ON" : "OFF",
                    ok ? "Enviado OK" : "Fallo MQTT");
    }
  }

  delay(5);
}
