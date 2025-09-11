import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QGridLayout, QSlider, QPushButton
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from gauges import HalfCircleGauge, StripGauge
from settings import Settings

class Devices(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("devices-container")
        self.control_widgets = []
        main_layout = QHBoxLayout(self)
        self.main_content = QWidget(); self.main_content.setObjectName("menu-box")
        self.main_content_layout = QVBoxLayout(self.main_content); self.main_content_layout.setAlignment(Qt.AlignTop)
        self._setup_ac_container(); self._setup_device_toggles(); self._setup_sliders(); self._setup_sidebar_gauges()
        main_layout.addWidget(self.main_content); main_layout.addWidget(self.sidebar_gauges_container)
        self.serial_read_timer = QTimer(self)
        self.serial_read_timer.timeout.connect(self.request_and_update_sensors)
        self.serial_read_timer.start(2000)
        self.set_controls_enabled(False)

    def request_and_update_sensors(self):
        if Settings.is_connected():
            Settings.send_command('S\n')
            QTimer.singleShot(100, self.read_and_process_data)

    def read_and_process_data(self):
        line = Settings.read_data()
        if line:
            try:
                if line.strip().startswith("{") and line.strip().endswith("}"):
                    sensor_data = json.loads(line)
                    self.update_gauges_from_dict(sensor_data)
            except json.JSONDecodeError: pass

    @pyqtSlot(bool)
    def set_controls_enabled(self, enabled):
        print(f"[DEVICES] Mengatur semua kontrol ke status: {'Aktif' if enabled else 'Nonaktif'}")
        for widget in self.control_widgets:
            widget.setEnabled(enabled)

    def update_gauges_from_dict(self, sensor_data):
        self.sidebar_temp_gauge.setTemperature(sensor_data.get("temp", 0))
        co2_val = sensor_data.get("co2", 0); self.sidebar_co2_gauge.setValue(co2_val // 20); self.sidebar_co2_value_label.setText(f"{co2_val} ppm")
        tvoc_val = sensor_data.get("tvoc", 0); self.sidebar_tvoc_gauge.setValue(min(tvoc_val // 10, 100)); self.sidebar_tvoc_value_label.setText(f"{tvoc_val} ppb")
        hum_val = sensor_data.get("hum", 0); self.sidebar_hum_gauge.setValue(int(hum_val)); self.sidebar_hum_value_label.setText(f"{hum_val:.1f}%")
        lux_val = sensor_data.get("lux", 0); self.sidebar_lux_gauge.setValue(min(int(lux_val) // 20, 100)); self.sidebar_lux_value_label.setText(f"{int(lux_val)} lux")

    def _setup_device_toggles(self):
        self.device_buttons_container = QWidget(); self.device_buttons_container.setObjectName("device-buttons-container")
        layout = QHBoxLayout(self.device_buttons_container)
        def create_toggle(label_text, cmd):
            vbox = QVBoxLayout(); vbox.setAlignment(Qt.AlignCenter)
            label = QLabel(label_text); label.setObjectName("toggle-label")
            btn = QPushButton("OFF"); btn.setCheckable(True); btn.setFixedSize(80, 38)
            btn.toggled.connect(lambda checked: btn.setText("ON" if checked else "OFF"))
            btn.toggled.connect(lambda checked, c=cmd: Settings.send_command(f"{c}{'1' if checked else '0'}\n"))
            vbox.addWidget(label); vbox.addWidget(btn)
            widget = QWidget(); widget.setLayout(vbox)
            self.control_widgets.append(btn)
            return widget
        layout.addWidget(create_toggle("UV Light", "U")); layout.addWidget(create_toggle("Indicator Light", "L"))
        layout.addWidget(create_toggle("Humidifier", "H")); layout.addWidget(create_toggle("Water Pump", "W"))
        self.main_content_layout.addWidget(self.device_buttons_container)

    def _setup_sliders(self):
        self.sliders_container = QWidget(); self.sliders_container.setObjectName("sliders-container")
        layout = QGridLayout(self.sliders_container)
        def create_slider(label_text, cmd, row, col):
            vbox = QVBoxLayout()
            label = QLabel(label_text); label.setObjectName("slider-label")
            slider = QSlider(Qt.Horizontal); slider.setRange(0, 255)
            value_label = QLabel(f"{slider.value()}")
            slider.valueChanged.connect(value_label.setNum)
            slider.sliderReleased.connect(lambda c=cmd, s=slider: Settings.send_command(f"{c}{s.value()}\n"))
            hbox = QHBoxLayout(); hbox.addWidget(slider); hbox.addWidget(value_label)
            vbox.addWidget(label); vbox.addLayout(hbox)
            widget = QWidget(); widget.setLayout(vbox)
            layout.addWidget(widget, row, col)
            self.control_widgets.append(slider)
        create_slider("Kipas Peltier", "P", 0, 0); create_slider("Kipas Radiator", "R", 0, 1)
        create_slider("Peltier PWM", "D", 1, 0); create_slider("Grow Light (Merah)", "G", 1, 1)
        create_slider("Grow Light (Biru)", "B", 2, 0)
        self.main_content_layout.addWidget(self.sliders_container)

    def _setup_ac_container(self):
        self.ac_container = QFrame(); self.ac_container.setObjectName("ac-container")
        ac_layout = QVBoxLayout(self.ac_container); ac_layout.setAlignment(Qt.AlignCenter)
        ac_top = QHBoxLayout(); ac_top.addWidget(QLabel("Air Conditioner"), alignment=Qt.AlignLeft); ac_top.addStretch()
        self.btn_ac_toggle = QPushButton("OFF"); self.btn_ac_toggle.setCheckable(True); self.btn_ac_toggle.setFixedSize(80, 36)
        ac_top.addWidget(self.btn_ac_toggle, alignment=Qt.AlignRight); ac_layout.addLayout(ac_top)
        ac_gauge_row = QHBoxLayout(); ac_gauge_row.setSpacing(16)
        self.btn_minus = QPushButton("▼"); self.btn_minus.setFixedSize(64, 64)
        self.ac_gauge = HalfCircleGauge()
        self.btn_plus = QPushButton("▲"); self.btn_plus.setFixedSize(64, 64)
        ac_gauge_row.addStretch(); ac_gauge_row.addWidget(self.btn_minus); ac_gauge_row.addWidget(self.ac_gauge); ac_gauge_row.addWidget(self.btn_plus); ac_gauge_row.addStretch()
        ac_layout.addLayout(ac_gauge_row); self.main_content_layout.addWidget(self.ac_container)
        self.control_widgets.extend([self.btn_ac_toggle, self.btn_minus, self.btn_plus])

    def _setup_sidebar_gauges(self):
        self.sidebar_gauges_container = QWidget(); self.sidebar_gauges_container.setObjectName("sidebar-gauges-container"); self.sidebar_gauges_container.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(self.sidebar_gauges_container)
        def create_strip_gauge_box(label_text, obj_name_prefix):
            box = QWidget(); box.setObjectName("gauge-box"); layout = QVBoxLayout(box)
            label = QLabel(label_text); label.setProperty("sensor-label", True); layout.addWidget(label, alignment=Qt.AlignCenter)
            gauge = StripGauge(); layout.addWidget(gauge)
            value_label = QLabel("N/A"); value_label.setObjectName("gauge-value-label"); layout.addWidget(value_label, alignment=Qt.AlignCenter)
            setattr(self, f"sidebar_{obj_name_prefix}_gauge", gauge); setattr(self, f"sidebar_{obj_name_prefix}_value_label", value_label)
            return box
        temp_box = QWidget(); temp_box.setObjectName("gauge-box"); temp_layout = QVBoxLayout(temp_box)
        temp_label = QLabel("🌡️ Temperature"); temp_label.setProperty("sensor-label", True); temp_layout.addWidget(temp_label, alignment=Qt.AlignCenter)
        self.sidebar_temp_gauge = HalfCircleGauge(); temp_layout.addWidget(self.sidebar_temp_gauge); sidebar_layout.addWidget(temp_box)
        sidebar_layout.addWidget(create_strip_gauge_box("🟢 CO₂ (ppm)", "co2")); sidebar_layout.addWidget(create_strip_gauge_box("🧪 TVOC (ppb)", "tvoc"))
        sidebar_layout.addWidget(create_strip_gauge_box("💧 Humidity (%)", "hum")); sidebar_layout.addWidget(create_strip_gauge_box("💡 Lux", "lux"))
        sidebar_layout.addStretch()