import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QLabel, QFrame
from PyQt5.QtGui import QIcon

from camera import Camera
from settings import Settings
from dashboard import Dashboard
from devices import Devices

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        icon_path = os.path.join(BASE_DIR, "Icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("R2C Smart Control UI")
        self.setGeometry(100, 100, 1280, 720)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self); self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)
        sidebar = self.create_sidebar(); main_layout.addWidget(sidebar)

        # Inisialisasi widget halaman
        self.settings_widget = Settings()
        self.dashboard_widget = Dashboard()
        self.devices_widget = Devices()
        self.camera_widget = Camera()
        
        # Hubungkan sinyal status koneksi dari Settings ke Devices
        self.settings_widget.connection_changed.connect(self.devices_widget.set_controls_enabled)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.dashboard_widget); self.stacked_widget.addWidget(self.devices_widget)
        self.stacked_widget.addWidget(self.camera_widget); self.stacked_widget.addWidget(self.settings_widget)
        main_layout.addWidget(self.stacked_widget, 1)

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
        self.camera_widget.cleanup() # Asumsi cleanup ada di camera.py
        self.settings_widget.disconnect_serial_port()
        print("Semua koneksi dihentikan. Keluar.")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    style_path = os.path.join(BASE_DIR, "style.qss")
    try:
        with open(style_path, "r") as f: app.setStyleSheet(f.read())
    except FileNotFoundError: print("Warning: style.qss not found.")
    window = MainWindow(); window.show()
    sys.exit(app.exec())