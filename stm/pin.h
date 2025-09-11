#ifndef PIN_H
#define PIN_H

#include "SparkFunCCS811.h"
#include <Adafruit_BME280.h>
#include <BH1750.h>
#include <Wire.h>

// =============== ALAMAT I2C =====================
#define TCA_ADDR 0x70          // Alamat I2C TCA9548A
#define CCS811_ADDR 0x5A       // Alamat I2C CCS811

// =============== PIN AKTUATOR (SESUAI GAMBAR) ====================
#define LIGHT        PB4     // PIN BARU UNTUK LAMPU INDIKATOR
#define UV_LIGHT     PB7     // Sesuai gambar
#define GROWLIGHT1   PB10    // Sesuai gambar
#define GROWLIGHT2   PA6     // Sesuai gambar
#define HUMIDIFIER   PB6     // PIN BERUBAH (sebelumnya PB5)
#define WATER_PUMP   PB5     // PIN BERUBAH (sebelumnya PB4)
#define RPWM_PELTIER PB15    // Sesuai gambar
#define LPWM_PELTIER PA8     // Sesuai gambar
#define FAN_PELTIER  PB13    // Sesuai gambar
#define FAN_RADIATOR PB14    // Sesuai gambar


/*
// Pin yang tidak ada di gambar (dinonaktifkan sementara)
#define damn         PB1
#define damns        PA4
*/


// =============== OBJEK SENSOR & LIBRARY =====================
// Objek sensor CCS811
CCS811 mySensor(CCS811_ADDR);

// SARAN: Buat dua objek terpisah untuk setiap tipe sensor
// karena Anda punya dua BME280 dan dua BH1750 di channel berbeda.
Adafruit_BME280 bme1; // Untuk sensor di channel 1
Adafruit_BME280 bme2; // Untuk sensor di channel 2

BH1750 lightMeter1;   // Untuk sensor di channel 1
BH1750 lightMeter2;   // Untuk sensor di channel 2


// // =============== VARIABEL PWM AWAL =====================
// int pwmPFan = 200;
// int pwmRFan = 0;
// int pwmGLed = 50;
// int pwmPelt = 210;
// int pwmGLed2 = 50;


// =============== FUNGSI HELPER =====================
// Fungsi untuk memilih channel pada TCA9548A
void TCA9548A(uint8_t bus) {
    Wire.beginTransmission(TCA_ADDR);
    Wire.write(1 << bus);  // Pilih channel
    Wire.endTransmission();
}

#endif // PIN_H