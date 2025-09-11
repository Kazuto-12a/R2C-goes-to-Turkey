import os
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QLabel, QFrame
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import paho.mqtt.client as mqtt
import json

from camera import Camera
from settings import Settings
from dashboard import Dashboard
from devices import Devices

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ===================================================================
# LANGKAH 1: BUAT KELAS WORKER UNTUK MQTT
# Kelas ini akan berjalan di background thread
# ===================================================================
class MqttClient(QObject):
    # Definisikan sinyal yang akan membawa data (string) dari thread ini ke thread utama
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTT Worker: Terhubung ke Broker!")
            client.subscribe("sensor/data")
        else:
            print(f"MQTT Worker: Gagal terhubung, kode: {rc}")

    def on_message(self, client, userdata, msg):
        # Saat pesan diterima, decode dan kirimkan melalui sinyal
        data = msg.payload.decode()
        self.message_received.emit(data)

    def run(self):
        """Mulai koneksi dan loop MQTT."""
        print("MQTT Worker: Memulai koneksi...")
        try:
            # Ganti localhost dengan IP Jetson Nano jika broker berjalan di sana
            self.client.connect("localhost", 1883, 60) 
            self.client.loop_forever()
        except Exception as e:
            print(f"MQTT Worker: Error - {e}")

# ===================================================================



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        icon_path = os.path.join(BASE_DIR, "Icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("R2C Smart Control UI")
        self.setGeometry(100, 100, 1280, 720)
        
        self.init_ui()
        self.init_mqtt() # Panggil fungsi untuk memulai MQTT

    def init_ui(self):
        central_widget = QWidget(self); self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)
        sidebar = self.create_sidebar(); main_layout.addWidget(sidebar)

        # Inisialisasi widget halaman
        self.settings_widget = Settings()# Inisialisasi MQTT Clientngs()
        self.dashboard_widget = Dashboard()
        self.devices_widget = Devices()
        self.camera_widget = Camera()
        
        # Hubungkan sinyal status koneksi dari Settings ke Devices
        self.settings_widget.connection_changed.connect(self.devices_widget.set_controls_enabled)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.dashboard_widget); self.stacked_widget.addWidget(self.devices_widget)
        self.stacked_widget.addWidget(self.camera_widget); self.stacked_widget.addWidget(self.settings_widget)
        main_layout.addWidget(self.stacked_widget, 1)

    # ===================================================================
    # LANGKAH 2: MODIFIKASI MAINWINDOW UNTUK MENGELOLA THREAD
    # ===================================================================
    def init_mqtt(self):
        # Buat thread baru
        self.mqtt_thread = QThread()
        # Buat instance worker MQTT
        self.mqtt_worker = MqttClient()
        # Pindahkan worker ke thread yang baru dibuat
        self.mqtt_worker.moveToThread(self.mqtt_thread)

        # Hubungkan sinyal thread 'started' ke fungsi 'run' di worker
        self.mqtt_thread.started.connect(self.mqtt_worker.run)
        
        # Hubungkan sinyal 'message_received' dari worker ke slot di MainWindow
        self.mqtt_worker.message_received.connect(self.update_gui_with_mqtt_data)
        
        # Mulai thread
        self.mqtt_thread.start()
        print("Main thread: Thread MQTT dimulai.")

    # ===================================================================
    # LANGKAH 3: BUAT SLOT UNTUK MEMPERBARUI GUI
    # ===================================================================
    def update_gui_with_mqtt_data(self, message):
        """Fungsi ini (slot) akan dijalankan di thread utama setiap kali ada data baru."""
        print(f"Main thread: Menerima data dari MQTT -> {message}")
        
        try:
            # Coba parsing data JSON
            data = json.loads(message)
            temp = data.get("temp", "N/A")
            hum = data.get("hum", "N/A")
            lux = data.get("lux", "N/A")
            
            # Sekarang Anda bisa mengupdate widget di dashboard Anda
            # CONTOH: (Asumsi Anda punya QLabel bernama temp_label di dashboard.py)
            # self.dashboard_widget.temp_label.setText(f"{temp}°C")
            # self.dashboard_widget.hum_label.setText(f"{hum}%")
            # self.dashboard_widget.lux_label.setText(f"{lux} lux")
            
        except json.JSONDecodeError:
            print(f"Main thread: Data diterima bukan format JSON yang valid: {message}")



    def create_sidebar(self):
        sidebar = QWidget(); sidebar.setObjectName("sidebar"); sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar); sidebar_layout.setContentsMargins(12, 18, 12, 12); sidebar_layout.setSpacing(8)
        project_label = QLabel("SMART CONTROL"); project_label.setObjectName("sidebar-label"); sidebar_layout.addWidget(project_label)
        divider = QFrame(); divider.setFrameShape(QFrame.HLine); divider.setFrameShadow(QFrame.Sunken); divider.setObjectName("sidebar-divider"); sidebar_layout.addWidget(divider)
        btn_dashboard = QPushButton("  🏠  Dashboard"); btn_devices = QPushButton("  🖥️  Devices")
        btn_camera = QPushButton("  📸  Camera"); btn_settings = QPushButton("  ⚙️  Settings")
        buttons = [btn_dashboard, btn_devices, btn_camera, btn_settings];
        for btn in buttons: sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch()
        btn_dashboard.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0)); btn_devices.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        btn_camera.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2)); btn_settings.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        btn_dashboard.setChecked(True)
        return sidebar

    def closeEvent(self, event):
        print("Menutup aplikasi...")
        # Hentikan thread MQTT dengan cara yang bersih
        if self.mqtt_thread.isRunning():
            print("Menghentikan thread MQTT...")
            self.mqtt_thread.quit()
            self.mqtt_thread.wait() # Tunggu sampai thread benar-benar berhenti
            print("Thread MQTT dihentikan.")

        self.camera_widget.cleanup()
        self.settings_widget.disconnect_serial_port()
        print("Semua koneksi dihentikan. Keluar.")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    style_path = os.path.join(BASE_DIR, "style.qss")
    # try:
    #     with open(style_path, "r") as f: app.setStyleSheet(f.read())
    # except FileNotFoundError: print("Warning: style.qss not found.")
    window = MainWindow(); window.show()
    sys.exit(app.exec())