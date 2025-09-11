// =================================================================
//                 PUSTAKA / LIBRARIES UTAMA
// =================================================================
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// --- Header Files Proyek Anda ---
#include "pin.h"
#include "sensor.h"
#include "aktuator.h"

// =================================================================
//                 PENGATURAN & OBJEK GLOBAL (KHUSUS MAIN)
// =================================================================

// --- Pengaturan OLED Display ---
#define OLED_RESET -1
Adafruit_SSD1306 display(OLED_RESET);

// --- Variabel untuk Timing Non-Blocking ---
unsigned long previousSensorReadMillis = 0;
unsigned long previousDisplayMillis = 0;
bool displaySesi1 = true;

// --- Interval Waktu (dalam milidetik) ---
const unsigned long SENSOR_READ_INTERVAL = 2000;
const unsigned long DISPLAY_SWITCH_INTERVAL = 4000;

// =================================================================
//                 FUNGSI SETUP UTAMA
// =================================================================
void setup() {
  Serial.begin(115200);
  Serial.println("\n--- Sistem Booting Up ---");

  // Inisialisasi I2C untuk STM32
  Wire.setSDA(PB9);
  Wire.setSCL(PB8);
  Wire.begin();

  // Inisialisasi display OLED (diasumsikan di channel 3)
  TCA9548A(3);
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("KRITIS: OLED tidak ditemukan!"));
    while (1);
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);
  display.println(F("Inisialisasi Sistem..."));
  display.display();
  delay(1000);

  // Panggil fungsi setup dari file header
  setup_aktuator();
  setup_sensor();
  
  Serial.println("--- Sistem Siap. Menunggu perintah... ---");
}

// =================================================================
//                 FUNGSI LOOP UTAMA
// =================================================================
void loop() {
  unsigned long currentMillis = millis();

  // TUGAS 1: Selalu dengarkan perintah dari Jetson
  kontrol_aktuator();

  // TUGAS 2: Baca sensor dan kirim data secara berkala
  if (currentMillis - previousSensorReadMillis >= SENSOR_READ_INTERVAL) {
    previousSensorReadMillis = currentMillis;
    baca_sensor();
    sendSensorDataToJetson(); // Kirim data JSON untuk Jetson
    printSensorToMonitor();   // FUNGSI BARU: Tampilkan data untuk debugging
  }

  // TUGAS 3: Update tampilan OLED secara berkala
  if (currentMillis - previousDisplayMillis >= DISPLAY_SWITCH_INTERVAL) {
    previousDisplayMillis = currentMillis;
    updateDisplay();
    displaySesi1 = !displaySesi1;
  }
}

// =================================================================
//                 FUNGSI PEMBANTU (MILIK MAIN)
// =================================================================

// Fungsi untuk mengirim data sensor dalam format JSON ke Jetson
void sendSensorDataToJetson() {
  String jsonString = "{";
  jsonString += "\"co2\":" + String(co2_val, 0) + ",";
  jsonString += "\"tvoc\":" + String(tvoc_val, 0) + ",";
  jsonString += "\"temp\":" + String(suhuAvg, 2) + ",";
  jsonString += "\"hum\":" + String(humAvg, 2) + ",";
  jsonString += "\"lux\":" + String(luxAvg, 1);
  jsonString += "}";
  Serial.println(jsonString);
}

// *** FUNGSI BARU UNTUK DEBUGGING DI SERIAL MONITOR ***
void printSensorToMonitor() {
  Serial.println("---[Nilai Sensor Terbaca]---");
  Serial.print("Suhu Avg: "); Serial.print(suhuAvg, 2); Serial.println(" C");
  Serial.print("Lembab Avg: "); Serial.print(humAvg, 2); Serial.println(" %");
  Serial.print("Cahaya Avg: "); Serial.print(luxAvg, 1); Serial.println(" Lux");
  Serial.print("CO2: "); Serial.print(co2_val, 0); Serial.println(" ppm");
  Serial.print("TVOC: "); Serial.print(tvoc_val, 0); Serial.println(" ppb");
  Serial.println("----------------------------");
}


// Fungsi khusus untuk mengupdate tampilan di layar OLED
void updateDisplay() {
  TCA9548A(3);
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);

  if (displaySesi1) {
    display.print("CO2: "); display.print(co2_val, 0); display.println(" ppm");
    display.setCursor(0, 12);
    display.print("TVOC: "); display.print(tvoc_val, 0); display.println(" ppb");
    display.setCursor(0, 24);
    display.print("Suhu: "); display.print(suhuAvg, 1); display.println(" C");
  } else {
    display.print("Lembab: "); display.print(humAvg, 1); display.println(" %");
    display.setCursor(0, 12);
    display.print("Cahaya: "); display.print(luxAvg, 0); display.println(" Lux");
  }
  display.display();
}