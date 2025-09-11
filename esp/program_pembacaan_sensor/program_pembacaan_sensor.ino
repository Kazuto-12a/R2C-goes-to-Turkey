#include "Global.h"

void setup() {
  Serial.begin(115200);
  Wire.begin();
  inisiasiawal();
}

void loop() {
  /* disable sensor buat test komunikasi
  // ---------------- read sensors -------------------- //
  lux = lightMeter.readLightLevel();    //Sensor Cahaya BH1750
  temp = bme.readTemperature();         // temp BME280
  hum = bme.readHumidity();             // humidity BME289
  eco2 = 0;                             // CCS811
  tvoc = 0;                             // CCS811
  ccs.setEnvironmentalData(hum, temp);  // Berikan data suhu dan kelembapan ke CCS811 untuk kompensasi

  // ------------ read CCS81 ------------ //
  if (ccs.dataAvailable()) {
    ccs.readAlgorithmResults();
    eco2 = ccs.getCO2();
    tvoc = ccs.getTVOC();
  }

  // ---------- Display Output ----------- //
  display_OLED();
  debug_Value();
*/
  // ------------------- Connect to MQTT -------------------- //
  send_data();
}