#include <Wire.h>
#include <BH1750.h>
#include <Adafruit_BME280.h>
#include "SparkFunCCS811.h"
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include <WiFi.h>
#include <PubSubClient.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

#define CCS811_ADDR 0x5A

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
BH1750 lightMeter;
Adafruit_BME280 bme;
CCS811 ccs(CCS811_ADDR);

// ----------- Global Variabel ----------------- //
float lux = 0;      //Sensor Cahaya BH1750
float temp = 0;     // temp BME280
float hum = 0;      // humidity BME289
uint16_t eco2 = 0;  // CCS811
uint16_t tvoc = 0;  // CCS811

// ---------- Setup MQTT ------------------ //
const char* ssid = "Kulkas Babe";
const char* password = "R2CJUARA";
const char* mqtt_server = "192.168.0.142";  // ip jetson

const char* mqtt_topic = "sensor/data";
const long interval = 500;  // kirim setiap 2 detik
unsigned long previousMillis = 0;

WiFiClient espClient;
PubSubClient client(espClient);


// --------------------- MQTT -------------------------- //
// adjust the ip address on esp32's code by typing "ip a" on jetson nano
// try to ping both esp32 and jetson nano ip address to debugging
// inactive the firewall, if it still won't connect
// last,
// do sudo nano /etc/mosquitto/mosquitto.conf and write "listener 1883 0.0.0.0"
// and "allow_anonymous true"

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Menghubungkan ke WiFi: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi terhubung!");
  Serial.print("Alamat IP ESP32: ");
  Serial.println(WiFi.localIP());
}

void reconnect_mqtt() {
  if (millis() - lastReconnectAttempt > 5000) {
    lastReconnectAttempt = millis();

    Serial.print("Mencoba terhubung ke MQTT Broker...");
    if (client.connect("ESP32Client")) {
      lastReconnectAttempt = 0;
      Serial.println("terhubung!");
    } else {
      Serial.print("gagal, rc=");
      Serial.print(client.state());
      Serial.println(" | Coba lagi dalam 5 detik");
    }
  }
}

void send_data() {
  if (!client.connected()) {
    reconnect_mqtt();
  }
  client.loop();

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // simulasi aja
    float temp = 25.72;
    float hum = 65.5;
    int lux = 850;
    int eco2 = 455;
    int tvoc = 15;
    float temperature = random(200, 350) / 10.0;  // Angka acak antara 20.0 dan 35.0

    if (client.connected()) {
      char payload[120];
      snprintf(payload, sizeof(payload), "{\"temp\":%.2f, \"hum\":%.1f,\"lux\":%d}", temperature, hum, lux);
      // snprintf(payload, sizeof(payload),
      //          "{\"temp\":%.2f, \"hum\":%.1f, \"lux\":%d, \"eco2\":%d, \"tvoc\":%d}",
      //          temp, hum, lux, eco2, tvoc);
      // Kirim data ke broker
      client.publish(mqtt_topic, payload);
      Serial.print("Data terkirim -> ");
      Serial.println(payload);
    } else {
      Serial.println("Koneksi MQTT terputus, data tidak dikirim.");
    }
  }
}


// ------------------ Setup() ------------------------- //
void inisiasiawal() {
  /*disable sensor buat test komunikasi
  // ----- setup OLED ------------------------
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("Gagal menginisialisasi SSD1306"));
    for (;;)
      ;
  }
  display.display();
  delay(1000);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Menginisialisasi sensor...");
  display.display();

  // setup  BH1750
  if (!lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println(F("Gagal menginisialisasi BH1750"));
  }

  // setup BME280
  if (!bme.begin(0x76)) {  // Cek alamat 0x76 atau 0x77
    Serial.println(F("Gagal menemukan sensor BME280"));
  }

  // settuo SparkFun CCS811
  if (ccs.begin() == false) {
    Serial.print("Gagal menginisialisasi CCS811. Cek alamat I2C dan koneksi.");
    while (1)
      ;
  }

  Serial.println("Semua sensor siap!");
  */
  // --------- setup wifi -------------
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  delay(1000);
}


// ------------------ Display to OLED ----------------- //
void display_OLED() {
  display.clearDisplay();
  display.setCursor(0, 0);

  display.print("Suhu: ");
  display.print(temp, 1);
  display.println(" C");
  display.print("Lembab: ");
  display.print(hum, 1);
  display.println(" %");
  display.print("Cahaya: ");
  display.print(lux, 0);
  display.println(" lx");
  display.println("--------------------");
  display.print("eCO2: ");
  display.print(eco2);
  display.println(" ppm");
  display.print("TVOC: ");
  display.print(tvoc);
  display.println(" ppb");

  display.display();
}

// ----------------- Serial Monitor Debug ------------ //
void debug_Value() {
  Serial.println("------------------------------");
  Serial.print("Suhu: ");
  Serial.print(temp, 1);
  Serial.println(" C");
  Serial.print("Kelembapan: ");
  Serial.print(hum, 1);
  Serial.println(" %");
  Serial.print("Cahaya: ");
  Serial.print(lux, 0);
  Serial.println(" lx");
  Serial.print("eCO2: ");
  Serial.print(eco2);
  Serial.println(" ppm");
  Serial.print("TVOC: ");
  Serial.print(tvoc);
  Serial.println(" ppb");
}