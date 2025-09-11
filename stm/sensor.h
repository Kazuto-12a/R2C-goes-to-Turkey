#ifndef SENSOR_H
#define SENSOR_H

// --- FAKTOR PENGHALUSAN DATA (0.0 - 1.0) ---
// Semakin kecil nilainya, semakin halus datanya, namun respon lebih lambat.
const float FILTER_ALPHA = 0.15;

// Variabel global untuk menyimpan nilai sensor yang sudah difilter
float suhu1, suhu2, suhuAvg, hum1, hum2, humAvg, lux1, lux2, luxAvg, co2_val, tvoc_val;

// =================================================================
//                 FUNGSI SETUP SENSOR
// =================================================================
// Menginisialisasi semua sensor pada channel I2C yang benar.
void setup_sensor(){
    Serial.println("--- Memulai Setup Sensor ---");

    // Inisialisasi sensor CCS811 (di channel 0)
    TCA9548A(0);
    Serial.print("Inisialisasi CCS811 di channel 0... ");
    if (!mySensor.begin()) {
        Serial.println("GAGAL! Periksa koneksi.");
        while (1); // Berhenti jika sensor utama gagal
    } else {
        Serial.println("BERHASIL!");
    }

    // Inisialisasi sensor SET 1 (di channel 1)
    TCA9548A(1);
    Serial.print("Inisialisasi BME280 #1 di channel 1... ");
    if (!bme1.begin(0x76)) { Serial.println("GAGAL!"); } else { Serial.println("BERHASIL!"); }

    Serial.print("Inisialisasi BH1750 #1 di channel 1... ");
    if (!lightMeter1.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) { Serial.println("GAGAL!"); } else { Serial.println("BERHASIL!"); }

    // Inisialisasi sensor SET 2 (di channel 2)
    TCA9548A(2);
    Serial.print("Inisialisasi BME280 #2 di channel 2... ");
    if (!bme2.begin(0x76)) { Serial.println("GAGAL!"); } else { Serial.println("BERHASIL!"); }

    Serial.print("Inisialisasi BH1750 #2 di channel 2... ");
    if (!lightMeter2.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) { Serial.println("GAGAL!"); } else { Serial.println("BERHASIL!"); }

    // Mengambil bacaan pertama untuk menginisialisasi nilai filter agar tidak mulai dari nol
    Serial.println("Mengambil bacaan sensor awal untuk inisialisasi filter...");
    delay(1000); // Beri waktu sensor untuk stabil setelah power on
    TCA9548A(0);
    if(mySensor.dataAvailable()){ mySensor.readAlgorithmResults(); co2_val = mySensor.getCO2(); tvoc_val = mySensor.getTVOC(); }
    TCA9548A(1); suhu1 = bme1.readTemperature(); hum1 = bme1.readHumidity(); lux1 = lightMeter1.readLightLevel();
    TCA9548A(2); suhu2 = bme2.readTemperature(); hum2 = bme2.readHumidity(); lux2 = lightMeter2.readLightLevel();
    
    Serial.println("--- Setup Sensor Selesai ---");
}


// =================================================================
//                 FUNGSI BACA SENSOR (DENGAN FILTER)
// =================================================================
// Membaca nilai dari semua sensor dan menghaluskannya menggunakan filter.
void baca_sensor(){
    // Pembacaan sensor CCS811 (channel 0)
    TCA9548A(0);
    if (mySensor.dataAvailable()) {
        mySensor.readAlgorithmResults();
        co2_val = (FILTER_ALPHA * mySensor.getCO2()) + ((1.0 - FILTER_ALPHA) * co2_val);
        tvoc_val = (FILTER_ALPHA * mySensor.getTVOC()) + ((1.0 - FILTER_ALPHA) * tvoc_val);
    }

    // Pembacaan sensor SET 1 (channel 1)
    TCA9548A(1);
    suhu1 = (FILTER_ALPHA * bme1.readTemperature()) + ((1.0 - FILTER_ALPHA) * suhu1);
    hum1 = (FILTER_ALPHA * bme1.readHumidity()) + ((1.0 - FILTER_ALPHA) * hum1);
    lux1 = (FILTER_ALPHA * lightMeter1.readLightLevel()) + ((1.0 - FILTER_ALPHA) * lux1);

    // Pembacaan sensor SET 2 (channel 2)
    TCA9548A(2);
    suhu2 = (FILTER_ALPHA * bme2.readTemperature()) + ((1.0 - FILTER_ALPHA) * suhu2);
    hum2 = (FILTER_ALPHA * bme2.readHumidity()) + ((1.0 - FILTER_ALPHA) * hum2);
    lux2 = (FILTER_ALPHA * lightMeter2.readLightLevel()) + ((1.0 - FILTER_ALPHA) * lux2);

    // Hitung nilai rata-rata dari data yang sudah difilter
    suhuAvg = ((suhu1 + suhu2) / 2.0) - 0.5; // Kalibrasi -0.5 tetap diterapkan
    humAvg = (hum1 + hum2) / 2.0;
    luxAvg = (lux1 + lux2) / 2.0;
}

#endif // SENSOR_H