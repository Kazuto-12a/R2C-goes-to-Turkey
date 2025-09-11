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


class MqttClient(QObject):
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
        data = msg.payload.decode()
        self.message_received.emit(data)

    def run(self):
        """Mulai koneksi dan loop MQTT."""
        print("MQTT Worker: Memulai koneksi...")
        try:
            self.client.connect("localhost", 1883, 60) 
            self.client.loop_forever()
        except Exception as e:
            print(f"MQTT Worker: Error - {e}")




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        icon_path = os.path.join(BASE_DIR, "Icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("R2C Smart Control UI")
        self.setGeometry(100, 100, 1280, 720)
        
        self.init_ui()
        self.init_mqtt()

    def init_ui(self):
        central_widget = QWidget(self); self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)
        sidebar = self.create_sidebar(); main_layout.addWidget(sidebar)

        self.settings_widget = Settings()
        self.dashboard_widget = Dashboard()
        self.devices_widget = Devices()
        self.camera_widget = Camera()
        
        self.settings_widget.connection_changed.connect(self.devices_widget.set_controls_enabled)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.dashboard_widget); self.stacked_widget.addWidget(self.devices_widget)
        self.stacked_widget.addWidget(self.camera_widget); self.stacked_widget.addWidget(self.settings_widget)
        main_layout.addWidget(self.stacked_widget, 1)

    def init_mqtt(self):
        self.mqtt_thread = QThread()
        self.mqtt_worker = MqttClient()
        self.mqtt_worker.moveToThread(self.mqtt_thread)

        self.mqtt_thread.started.connect(self.mqtt_worker.run)
        self.mqtt_worker.message_received.connect(self.update_gui_with_mqtt_data)
        
        self.mqtt_thread.start()
        print("Main thread: Thread MQTT dimulai.")


    def update_gui_with_mqtt_data(self, message):
        """Fungsi ini (slot) akan dijalankan di thread utama setiap kali ada data baru."""
        print(f"Main thread: Menerima data dari MQTT -> {message}")
        
        try:
            parts = message.split(',')
            
            if len(parts) == 5:
                temp = float(parts[0])
                hum = float(parts[1])
                lux = int(parts[2])
                eco2 = int(parts[3])
                tvoc = int(parts[4])
                
                print(f"Data Parsed -> Temp: {temp}, Hum: {hum}, Lux: {lux}, eCO2: {eco2}, TVOC: {tvoc}")
            
                self.dashboard_widget.update_sensor_data(temp, hum, lux, eco2, tvoc)
                
            else:
                print(f"Main thread: Format data tidak sesuai, jumlah bagian: {len(parts)}")
                
        except (ValueError, IndexError) as e:
            print(f"Main thread: Error saat mem-parse data: {e}")



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
        if self.mqtt_thread.isRunning():
            print("Menghentikan thread MQTT...")
            self.mqtt_thread.quit()
            self.mqtt_thread.wait()
            print("Thread MQTT dihentikan.")

        self.camera_widget.cleanup()
        self.settings_widget.disconnect_serial_port()
        print("Semua koneksi dihentikan. Keluar.")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    style_path = os.path.join(BASE_DIR, "style.qss")
    window = MainWindow(); window.show()
    sys.exit(app.exec())