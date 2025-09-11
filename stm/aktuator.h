#ifndef AKTUATOR_H
#define AKTUATOR_H

// Forward declaration untuk fungsi yang ada di file .ino utama
// Ini memberitahu compiler bahwa fungsi ini ada di tempat lain.
void sendSensorDataToJetson();

// Definisikan pin untuk lampu indikator
#define LIGHT        PB4     // PIN BARU UNTUK LAMPU INDIKATOR

// =================================================================
//                 FUNGSI SETUP AKTUATOR
// =================================================================
void setup_aktuator() {
    // Setup pin modes untuk semua aktuator
    pinMode(LIGHT, OUTPUT);   // Setup pin untuk lampu indikator
    pinMode(UV_LIGHT, OUTPUT);
    pinMode(GROWLIGHT1, OUTPUT); // Pin untuk PWM Grow Light 1 (Merah)
    pinMode(GROWLIGHT2, OUTPUT); // Pin untuk PWM Grow Light 2 (Biru)
    pinMode(HUMIDIFIER, OUTPUT);
    pinMode(WATER_PUMP, OUTPUT);
    pinMode(RPWM_PELTIER, OUTPUT);
    pinMode(LPWM_PELTIER, OUTPUT);
    pinMode(FAN_PELTIER, OUTPUT);
    pinMode(FAN_RADIATOR, OUTPUT);

    // Set kondisi awal (default) untuk semua aktuator saat startup
    digitalWrite(LIGHT, LOW);      // Lampu indikator menyala saat HIGH
    digitalWrite(UV_LIGHT, LOW);    // Relay ON saat LOW (aktif LOW, jadi OFF saat HIGH)
    digitalWrite(HUMIDIFIER, LOW);  // Relay ON saat LOW (aktif LOW, jadi OFF saat HIGH)
    digitalWrite(WATER_PUMP, LOW);  // Relay ON saat LOW (aktif LOW, jadi OFF saat HIGH)
   // digitalWrite(LPWM_PELTIER, LOW);  // Relay ON saat LOW (aktif LOW, jadi OFF saat HIGH)
    // Set nilai awal untuk semua aktuator PWM ke 0 (mati)
    analogWrite(GROWLIGHT1, 0);
    analogWrite(GROWLIGHT2, 0);
    
    // Set nilai awal untuk aktuator PWM lainnya sesuai kebutuhan
    analogWrite(RPWM_PELTIER, 185);
    digitalWrite(LPWM_PELTIER, 0);
    analogWrite(FAN_PELTIER, 255);
    analogWrite(FAN_RADIATOR, 255);
}

// =================================================================
//                 FUNGSI KONTROL AKTUATOR
// =================================================================
// Mendengarkan perintah dari Serial (Jetson) dan menggerakkan aktuator.
void kontrol_aktuator() {
    if (Serial.available() > 0) {
        char commandChar = Serial.read(); // Baca karakter perintah utama

        switch (commandChar) {
            case 'S': // Perintah untuk meminta data sensor
                sendSensorDataToJetson();
                break;

            // --- KONTROL ON/OFF (HIGH = ON, LOW = OFF) ---
            case 'U': // Kontrol UV Light (U1/U0)
                if (Serial.read() == '1') { digitalWrite(UV_LIGHT, HIGH); Serial.println("UV Light ON"); }
                else { digitalWrite(UV_LIGHT, LOW); Serial.println("UV Light OFF"); }
                break;

            case 'H': // Kontrol Humidifier (H1/H0)
                if (Serial.read() == '1') { digitalWrite(HUMIDIFIER, HIGH); Serial.println("Humidifier ON"); }
                else { digitalWrite(HUMIDIFIER, LOW); Serial.println("Humidifier OFF"); }
                break;

            case 'W': // Kontrol Water Pump (W1/W0)
                if (Serial.read() == '1') { digitalWrite(WATER_PUMP, HIGH); Serial.println("Water Pump ON"); }
                else { digitalWrite(WATER_PUMP, LOW); Serial.println("Water Pump OFF"); }
                break;

            // --- KONTROL LAMPU INDIKATOR (L1 = ON, L0 = OFF) ---
            case 'L': // Kontrol Lampu Indikator (L1/L0)
                if (Serial.read() == '1') { 
                    digitalWrite(LIGHT, HIGH); 
                    Serial.println("Lampu Indikator ON");
                }
                else { 
                    digitalWrite(LIGHT, LOW); 
                    Serial.println("Lampu Indikator OFF");
                }
                break;

            // --- KONTROL PWM ---
            case 'P': // Set Kipas Peltier speed
            case 'R': // Set Kipas Radiator speed
            case 'D': // Set Peltier PWM
            case 'G': // Set Grow Light 1 (Merah) PWM
            case 'B': // Set Grow Light 2 (Biru) PWM
                {
                    // Metode andal untuk membaca nilai integer dari serial
                    int value = Serial.parseInt(); 
                    
                    // Batasi nilai yang diterima antara 0 dan 255
                    value = constrain(value, 0, 255); 

                    if (commandChar == 'P') { analogWrite(FAN_PELTIER, value); Serial.print("Kipas Peltier speed: "); Serial.println(value); }
                    else if (commandChar == 'R') { analogWrite(FAN_RADIATOR, value); Serial.print("Kipas Radiator speed: "); Serial.println(value); }
                    else if (commandChar == 'D') { analogWrite(RPWM_PELTIER, value); Serial.print("Peltier PWM: "); Serial.println(value); }
                    else if (commandChar == 'G') { analogWrite(GROWLIGHT1, value); Serial.print("Grow Light 1 (Merah) PWM: "); Serial.println(value); }
                    else if (commandChar == 'B') { analogWrite(GROWLIGHT2, value); Serial.print("Grow Light 2 (Biru) PWM: "); Serial.println(value); }
                }
                break;
        }

        // Buang sisa data di buffer untuk mencegah perintah error pada loop berikutnya
        while(Serial.available() > 0) {
            Serial.read();
        }
    }
}

#endif // AKTUATOR_H
