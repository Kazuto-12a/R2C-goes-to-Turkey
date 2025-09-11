import paho.mqtt.client as mqtt

# Konfigurasi Broker dan Topik
# "localhost" berarti broker MQTT berjalan di mesin yang sama dengan skrip ini.
MQTT_BROKER = "localhost"
MQTT_TOPIC = "sensor/data"

# Fungsi ini akan dijalankan saat skrip berhasil terhubung ke broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Terhubung ke Broker MQTT Lokal!")
        # Langsung subscribe ke topik saat terhubung
        client.subscribe(MQTT_TOPIC)
        print(f"Mendengarkan topik: '{MQTT_TOPIC}'")
    else:
        print(f"Gagal terhubung, kode hasil: {rc}")

# Fungsi ini akan dijalankan setiap kali ada pesan baru di topik yang kita dengarkan
def on_message(client, userdata, msg):
    # msg.payload berisi data dari ESP32 (dalam format bytes), kita decode menjadi teks
    data = msg.payload.decode()
    print(f"Data diterima: {data}")
    # Anda bisa menambahkan kode untuk memproses data ini lebih lanjut

# Inisialisasi MQTT Client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

# Coba hubungkan ke broker
try:
    client.connect(MQTT_BROKER, 1883, 60)
except ConnectionRefusedError:
    print("Koneksi ditolak. Pastikan broker Mosquitto sudah berjalan.") 
    exit()
except OSError:
    print("Tidak dapat terhubung. Pastikan alamat broker sudah bena r.")
    exit()


# loop_forever() akan membuat skrip berjalan terus untuk mendengarkan pesan
client.loop_forever()