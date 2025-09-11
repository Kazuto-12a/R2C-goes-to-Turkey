from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QSpacerItem
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QPixmap
import requests

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("main-menu-container")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Dashboard Top Section ---
        top_widget = QWidget()
        top_widget.setObjectName("dashboard-top")
        top_widget.setMinimumSize(560, 130)
        # top_widget.setMaximumSize(560, 130)
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(24, 24, 24, 24)
        top_layout.setSpacing(16)

        # Overlay container for text (for readability)
        overlay_widget = QWidget(top_widget)
        overlay_widget.setObjectName("dashboard-overlay")
        overlay_layout = QHBoxLayout(overlay_widget)
        overlay_layout.setContentsMargins(24, 16, 24, 16)  # Add padding inside overlay
        overlay_layout.setSpacing(32)  # More space between left and right

        # Left: Greeting and subtext
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        greeting_label = QLabel("Hi, R2C! Good Evening...")
        greeting_label.setObjectName("greeting-label")
        greeting_label.setStyleSheet("font-weight: bold; font-size: 18px; color: white;")
        subtext_label = QLabel("Welcome Home.")
        subtext_label.setStyleSheet("font-family: Arial; font-size: 16px; font-weight: bold; color: white;")
        left_layout.addWidget(greeting_label)
        left_layout.addWidget(subtext_label)
        left_layout.addStretch()

        # Right: Realtime Date, Time, Temperature
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Time label
        self.time_label = QLabel()
        self.time_label.setStyleSheet("font-size: 20px; color: white; font-weight: bold;")
        right_layout.addWidget(self.time_label)

        # Date label
        self.date_label = QLabel()
        self.date_label.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        right_layout.addWidget(self.date_label)

        # Temperature label (simulate, or replace with real sensor data)
        self.temp_label = QLabel("")
        self.temp_label.setStyleSheet("font-size: 18px; color: white; margin-top: 8px;")
        self.temp_label.setMinimumWidth(180)  # Increased width
        self.temp_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.temp_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.temp_label.setWordWrap(False)
        right_layout.addWidget(self.temp_label)

        right_layout.addStretch()

        # Timer for time and date (every second)
        timer_datetime = QTimer(self)
        timer_datetime.timeout.connect(self.update_datetime)
        timer_datetime.start(1000)
        self.update_datetime()

        # Timer for temperature (every 10 minutes)
        timer_temp = QTimer(self)
        timer_temp.timeout.connect(self.update_temperature)
        timer_temp.start(600000)  # 600,000 ms = 10 minutes
        self.update_temperature()  # Initial fetch

        overlay_layout.addLayout(left_layout)
        overlay_layout.addLayout(right_layout)  # Remove the addStretch() between them

        # Optionally, set a minimum size for the overlay to cover more area
        overlay_widget.setMinimumHeight(100)
        overlay_widget.setMinimumWidth(500)

        top_layout.addWidget(overlay_widget)

        # Set overlay background for readability
        overlay_widget.setStyleSheet("""
            QWidget#dashboard-overlay {
                background-color: rgba(30, 40, 60, 210);  /* slightly less transparent */
                border-radius: 18px;
            }
        """)

        # Optionally set a background image or color for top_widget
        top_widget.setStyleSheet(f"""
            QWidget#dashboard-top {{
                background-color: #3a5a7a;
                background-image: url("wallpaper3.jpg");
                background-position: center;
                background-repeat: no-repeat;
                border-radius: 24px;
                padding: 8px;
                color: white;
                border: 4px solid #223344;
            }}
        """)

        # --- Right Side Container ---
        right_side_widget = QWidget()
        right_side_widget.setObjectName("dashboard-right")
        right_side_widget.setMinimumSize(280, 130)
        # right_side_widget.setMaximumSize(240, 130)
        right_side_widget.setStyleSheet("""
            QWidget#dashboard-right {
                background-color: #ffffff;
                border-radius: 24px;
                color: #222;
                border: 4px solid #e0e0e0; /* Subtle grey border */
            }
        """)
        right_side_layout = QVBoxLayout(right_side_widget)
        right_side_layout.setContentsMargins(16, 16, 16, 16)
        right_side_layout.setSpacing(8)

        # Add resizeable logo and text next to it
        logo_row = QHBoxLayout()
        logo_row.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center horizontally

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setMinimumSize(0, 0)  # Allow full shrinking
        logo_label.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        self.logo_pixmap = QPixmap("UKSW.png")
        logo_label.setPixmap(self.logo_pixmap.scaled(70, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        text_label = QLabel("R2C SWCU")
        text_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        text_label.setStyleSheet("font-family: Arial; font-weight: bold; font-size: 20px; color: #223344; margin-left: 12px;")

        logo_row.addWidget(logo_label, 0)
        logo_row.addWidget(text_label, 1)

        # Remove logo_row.addStretch() to keep content centered

        right_side_layout.addStretch()
        right_side_layout.addLayout(logo_row)
        right_side_layout.addStretch()

        # --- Main Top Row Layout ---
        top_row_layout = QHBoxLayout()
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.setSpacing(16)
        top_row_layout.addWidget(top_widget)
        top_row_layout.addWidget(right_side_widget)

        main_layout.addLayout(top_row_layout)
        main_layout.addStretch()

        # --- Main Content Container ---
        main_content_widget = QWidget()
        main_content_widget.setObjectName("main-content")
        main_content_widget.setMinimumSize(0, 300)  # Set a minimum height if you want
        main_content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_content_widget.setStyleSheet("""
            QWidget#main-content {
                background-color: #f7f7f7;
                border-radius: 20px;
                border: 2px solid #e0e0e0;
            }
        """)
        main_content_layout = QVBoxLayout(main_content_widget)
        main_content_layout.setContentsMargins(32, 32, 32, 32)
        main_content_layout.setSpacing(16)

        # Example placeholder content
        placeholder_label = QLabel("Main Content Area")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("font-size: 22px; color: #888;")
        main_content_layout.addWidget(placeholder_label)

        # Add the main content container to the main layout
        main_layout.addWidget(main_content_widget)
        main_layout.addStretch()

        # Make logo resize with the container, but keep it a bit smaller
        original_resize_event = right_side_widget.resizeEvent

        self.logo_label = logo_label
        self.logo_manual_size = 100  # None means auto

        right_side_widget.resizeEvent = self.resize_logo

    def update_datetime(self):
        now = QDateTime.currentDateTime()
        self.date_label.setText(now.toString("dddd, dd MMMM yyyy"))
        self.time_label.setText(now.toString("HH:mm:ss"))

    def update_temperature(self):
        # Example: Get temperature for Jakarta, Indonesia (lat: -6.2, lon: 106.8)
        # You can change these coordinates to match the user's country/city
        lat, lon = -6.2, 106.8
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            response = requests.get(url, timeout=5)
            data = response.json()
            temp = data["current_weather"]["temperature"]
            self.temp_label.setText(f"🌡️ {temp}°C")
        except Exception:
            self.temp_label.setText("🌡️ N/A")

    def set_logo_size(self, size):
        """Manually set the logo size (width and height in px)."""
        self.logo_manual_size = size
        if size > 0 and not self.logo_pixmap.isNull():
            self.logo_label.setPixmap(
                self.logo_pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )

    def resize_logo(self, event):
        if self.logo_manual_size:
            size = self.logo_manual_size
        else:
            size = int((min(self.logo_label.parent().width(), self.logo_label.parent().height()) - 32) * 0.7)
        if size > 0 and not self.logo_pixmap.isNull():
            self.logo_label.setPixmap(
                self.logo_pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
        # Call the original event if needed
        # super(type(self.logo_label.parent()), self.logo_label.parent()).resizeEvent(event)
