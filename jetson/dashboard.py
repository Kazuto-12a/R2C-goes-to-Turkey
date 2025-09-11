from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QGridLayout
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QPixmap

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("main-menu-container")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18) # Beri sedikit margin
        main_layout.setSpacing(18)

        # --- Top Row (Welcome Banner + Logo) ---
        self.setup_top_row(main_layout)

        # --- Main Content (Sensor Grid) ---
        self.setup_sensor_grid(main_layout)

        main_layout.addStretch()

    def setup_top_row(self, parent_layout):
        # ... (Kode untuk bagian atas, seperti greeting, jam, dan logo, tidak perlu diubah signifikan) ...
        # ... Saya akan sedikit menyederhanakannya untuk fokus pada data sensor ...
        
        top_row_layout = QHBoxLayout()
        top_widget = QWidget()
        top_widget.setObjectName("dashboard-top")
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(24, 16, 24, 16)

        # Left: Greeting, Time, Date
        left_layout = QVBoxLayout()
        greeting_label = QLabel("Selamat Datang, R2C!")
        greeting_label.setObjectName("greeting-label")
        self.time_label = QLabel()
        self.time_label.setObjectName("time-label")
        self.date_label = QLabel()
        self.date_label.setObjectName("date-label")
        left_layout.addWidget(greeting_label)
        left_layout.addWidget(self.time_label)
        left_layout.addWidget(self.date_label)
        
        # Right: Temperature (akan diupdate dari MQTT)
        # KITA PINDAHKAN LABEL SUHU KE SINI
        self.temp_label = QLabel("🌡️ -- °C")
        self.temp_label.setObjectName("temp-label-main")
        
        top_layout.addLayout(left_layout, 2) # Beri lebih banyak ruang untuk teks
        top_layout.addStretch(1)
        top_layout.addWidget(self.temp_label, 1)

        timer_datetime = QTimer(self)
        timer_datetime.timeout.connect(self.update_datetime)
        timer_datetime.start(1000)
        self.update_datetime()

        parent_layout.addWidget(top_widget)

    def setup_sensor_grid(self, parent_layout):
        """Membuat grid untuk menampilkan data sensor utama."""
        content_widget = QWidget()
        content_widget.setObjectName("main-content")
        content_layout = QGridLayout(content_widget)
        content_layout.setSpacing(20)

        # --- Membuat Label untuk setiap sensor ---
        self.hum_label = self.create_sensor_label("-- %")
        self.lux_label = self.create_sensor_label("-- lux")
        self.eco2_label = self.create_sensor_label("-- ppm")
        self.tvoc_label = self.create_sensor_label("-- ppb")
        
        # --- Menambahkan widget ke grid ---
        # Format: (widget, baris, kolom, rowspan, colspan)
        content_layout.addWidget(self.create_title_label("💧 Kelembapan"), 0, 0)
        content_layout.addWidget(self.hum_label, 1, 0)
        
        content_layout.addWidget(self.create_title_label("☀️ Intensitas Cahaya"), 0, 1)
        content_layout.addWidget(self.lux_label, 1, 1)

        content_layout.addWidget(self.create_title_label("💨 eCO2 (Karbon Dioksida)"), 2, 0)
        content_layout.addWidget(self.eco2_label, 3, 0)

        content_layout.addWidget(self.create_title_label("🌿 TVOC (Senyawa Organik)"), 2, 1)
        content_layout.addWidget(self.tvoc_label, 3, 1)

        parent_layout.addWidget(content_widget)

    def create_title_label(self, text):
        """Helper function untuk membuat label judul sensor."""
        label = QLabel(text)
        label.setObjectName("sensor-title-label")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def create_sensor_label(self, initial_text):
        """Helper function untuk membuat label nilai sensor."""
        label = QLabel(initial_text)
        label.setObjectName("sensor-value-label")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def update_datetime(self):
        now = QDateTime.currentDateTime()
        self.date_label.setText(now.toString("dddd, dd MMMM yyyy"))
        self.time_label.setText(now.toString("HH:mm:ss"))
    
    # ===================================================================
    # FUNGSI KUNCI: Dipanggil dari main.py untuk update data
    # ===================================================================
    def update_sensor_data(self, temp, hum, lux, eco2, tvoc):
        """Memperbarui semua label sensor dengan data baru."""
        self.temp_label.setText(f"🌡️ {temp:.1f}°C")
        self.hum_label.setText(f"{hum:.1f} %")
        self.lux_label.setText(f"{lux} lux")
        self.eco2_label.setText(f"{eco2} ppm")
        self.tvoc_label.setText(f"{tvoc} ppb")
    # ===================================================================