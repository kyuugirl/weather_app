import sys
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QStackedLayout, QGridLayout, QScrollArea
)
from PyQt6.QtGui import (
    QPixmap, QMovie, QFont
)
from PyQt6.QtCore import Qt, QTimer

import pygame
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(BASE_DIR, "config.json")

def get_asset(path):
    return os.path.join(BASE_DIR, path)

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather App")
        self.resize(1280, 720)

        # Start audio engine
        pygame.mixer.init()

        # Two modes: layout 1 and layout 2
        self.layout_stack = QStackedLayout()
        self.setLayout(self.layout_stack)

        # Layer: main background image
        self.background_label = QLabel(self)
        self.background_label.setScaledContents(True)
        self.background_label.lower()

        # Layer: rain/snow effect GIF
        self.effect_label = QLabel(self)
        self.effect_label.setScaledContents(True)
        self.effect_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.effect_label.raise_()

        # Weather icon (GIF supported)
        self.weather_icon = QLabel()
        self.weather_icon.setFixedSize(120, 120)

        # Create the two UI layouts
        self.layout_one_widget = self.build_layout_one()
        self.layout_two_widget = self.build_layout_two()

        self.layout_stack.addWidget(self.layout_one_widget)
        self.layout_stack.addWidget(self.layout_two_widget)

        # Build dynamic hourly strip container (will be replaced when updated)
        self.hour_strip_widget = None

        # Timers
        self.init_timers()

        # Initial calls
        self.update_background()
        self.update_weather_display()
        self.update_effect_gif()
        self.update_music()
        self.update_forecast_strip()

    # ================================================================
    # LAYOUT ONE (matches screenshot layout 1)
    # ================================================================
    def build_layout_one(self):
        container = QWidget()
        main_v = QVBoxLayout(container)

        top_row = QHBoxLayout()
        self.temp_label_1 = QLabel("0°C")
        self.temp_label_1.setFont(QFont("Arial", 48))
        self.temp_label_1.setStyleSheet("color:white;")

        self.condition_label_1 = QLabel("Condition")
        self.condition_label_1.setFont(QFont("Arial", 20))
        self.condition_label_1.setStyleSheet("color:white;")

        icon_col = QVBoxLayout()
        icon_col.addWidget(self.weather_icon)
        icon_col.addWidget(self.condition_label_1)

        top_row.addWidget(self.temp_label_1)
        top_row.addLayout(icon_col)
        main_v.addLayout(top_row)

        # Hourly scroll strip placeholder
        self.hour_strip_placeholder_1 = QVBoxLayout()
        main_v.addLayout(self.hour_strip_placeholder_1)

        # Weekly forecast
        main_v.addWidget(self.build_weekly_table())

        # Hourly text forecast
        main_v.addWidget(self.build_hourly_panel())

        return container

    # ================================================================
    # LAYOUT TWO (matches screenshot layout 2)
    # ================================================================
    def build_layout_two(self):
        container = QWidget()
        main_v = QVBoxLayout(container)

        top_row = QHBoxLayout()
        self.temp_label_2 = QLabel("0°C")
        self.temp_label_2.setFont(QFont("Arial", 48))
        self.temp_label_2.setStyleSheet("color:white;")

        self.condition_label_2 = QLabel("Condition")
        self.condition_label_2.setFont(QFont("Arial", 20))
        self.condition_label_2.setStyleSheet("color:white;")

        top_row.addWidget(self.temp_label_2)
        top_row.addWidget(self.condition_label_2)
        main_v.addLayout(top_row)

        # Hour strip placeholder
        self.hour_strip_placeholder_2 = QVBoxLayout()
        main_v.addLayout(self.hour_strip_placeholder_2)

        # Weekly forecast (different placement)
        main_v.addWidget(self.build_weekly_table())

        # Hourly forecast panel
        main_v.addWidget(self.build_hourly_panel())

        return container

    # ================================================================
    # WEEKLY FORECAST (transparent)
    # ================================================================
    def build_weekly_table(self):
        wrapper = QWidget()
        wrapper.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        grid = QGridLayout(wrapper)
        self.week_labels = []

        for i in range(7):
            circle = QLabel()
            circle.setFixedSize(70, 70)
            circle.setStyleSheet("background-color: rgba(255,255,255,30); border-radius: 35px;")

            day_lbl = QLabel(f"D{i+1}")
            day_lbl.setStyleSheet("color:white;")
            day_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            v = QVBoxLayout()
            v.addWidget(circle)
            v.addWidget(day_lbl)

            w = QWidget()
            w.setLayout(v)
            w.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            grid.addWidget(w, 0, i)
            self.week_labels.append(day_lbl)

        return wrapper

    # ================================================================
    # HOURLY FORECAST TEXT PANEL
    # ================================================================
    def build_hourly_panel(self):
        wrapper = QWidget()
        wrapper.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        v = QVBoxLayout(wrapper)
        self.hourly_labels = []

        for _ in range(5):
            lbl = QLabel("Time – forecast")
            lbl.setStyleSheet("color:white;")
            v.addWidget(lbl)
            self.hourly_labels.append(lbl)

        return wrapper

    # ================================================================
    # DYNAMIC HOURLY SCROLL STRIP
    # ================================================================
    def build_dynamic_hour_strip(self, forecast_times):
        """
        forecast_times: list of timestamps or datetime objects.
        """

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        h = QHBoxLayout(container)

        self.hour_bg_labels = []

        for entry in forecast_times:
            if isinstance(entry, str):
                dt = datetime.fromisoformat(entry)
            else:
                dt = entry

            hour = dt.hour

            img_label = QLabel()
            img_label.setFixedSize(250, 150)
            img_label.setScaledContents(True)

            # === YOUR LOGIC HERE ===
            # pull correct background image for this hour
            bg_path = f"backgrounds/{hour}.jpg"

            pix = QPixmap(bg_path).scaled(250, 150, Qt.AspectRatioMode.IgnoreAspectRatio)
            img_label.setPixmap(pix)

            text_label = QLabel(f"{hour:02d}:00")
            text_label.setStyleSheet("color:white;")

            w = QWidget()
            v = QVBoxLayout(w)
            v.addWidget(img_label)
            v.addWidget(text_label)

            h.addWidget(w)
            self.hour_bg_labels.append(img_label)

        scroll.setWidget(container)
        return scroll

    # ================================================================
    # TIMERS
    # ================================================================
    def init_timers(self):
        bg_timer = QTimer(self)
        bg_timer.timeout.connect(self.update_background)
        bg_timer.start(60_000)

        weather_timer = QTimer(self)
        weather_timer.timeout.connect(self.update_weather_display)
        weather_timer.start(60_000)

        effect_timer = QTimer(self)
        effect_timer.timeout.connect(self.update_effect_gif)
        effect_timer.start(60_000)

        strip_timer = QTimer(self)
        strip_timer.timeout.connect(self.update_forecast_strip)
        strip_timer.start(60_000)

    # ================================================================
    # MAIN BACKGROUND (real-time hour)
    # ================================================================
    def update_background(self):
        hour = datetime.now().hour
        path = get_asset("assets/bgs/snowy.jpg")#f"backgrounds/{hour}.jpg"   # === YOUR LOGIC HERE ===


        pix = QPixmap(path).scaled(self.width(), self.height(), Qt.AspectRatioMode.IgnoreAspectRatio)
        self.background_label.setPixmap(pix)

    # ================================================================
    # WEATHER DISPLAY (API)
    # ================================================================
    def update_weather_display(self):
        # === YOUR LOGIC HERE ===
        # Example placeholder:
        temp = 22
        condition = "Clear"

        self.temp_label_1.setText(f"{temp}°C")
        self.temp_label_2.setText(f"{temp}°C")
        self.condition_label_1.setText(condition)
        self.condition_label_2.setText(condition)

        # Set animated weather icon
        icon_path = f"icons/{condition.lower()}.gif"   # === YOUR LOGIC HERE ===

        try:
            movie = QMovie(icon_path)
            self.weather_icon.setMovie(movie)
            movie.start()
        except:
            pass

    # ================================================================
    # WEATHER EFFECTS LAYER (RAIN/SNOW GIF)
    # ================================================================
    def update_effect_gif(self):
        # === YOUR LOGIC HERE ===
        condition = "rain"   # Replace with real condition

        gif_map = {
            "rain": get_asset("assets/effects/rain.gif"),
            "snow": get_asset("assets/effects/snow.gif"),
        }

        if condition.lower() in gif_map:
            movie = QMovie(gif_map[condition.lower()])
            self.effect_label.setMovie(movie)
            movie.start()
            self.effect_label.resize(self.size())
        else:
            self.effect_label.clear()

    # ================================================================
    # MUSIC BY WEATHER
    # ================================================================
    def update_music(self):
        # === YOUR LOGIC HERE ===
        condition = "Clear"   # Replace with API data

        tracks = {
            "clear": "music/clear.mp3",
            "rain": "music/rain.mp3",
            "snow": "music/snow.mp3"
        }

        track = get_asset("assets/music/sun.mp3")#tracks.get(condition.lower(), "music/default.mp3")
        pygame.mixer.music.load(track)
        pygame.mixer.music.play(-1)

    # ================================================================
    # UPDATE THE HOURLY STRIP (data-driven)
    # ================================================================
    def update_forecast_strip(self):
        """
        Pull intervals from API, build new hourly strip.
        """

        # === YOUR LOGIC HERE ===
        # Replace with your real forecast.
        # The list can represent ANY interval (1h, 3h, 6h, etc.)
        forecast_times = [
            "2025-01-30 09:00",
            "2025-01-30 12:00",
            "2025-01-30 15:00",
            "2025-01-30 18:00",
            "2025-01-30 21:00",
        ]

        new_strip = self.build_dynamic_hour_strip(forecast_times)

        # Replace strip in BOTH layouts
        for placeholder in [self.hour_strip_placeholder_1, self.hour_strip_placeholder_2]:
            # Remove old widget if exists
            while placeholder.count():
                item = placeholder.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()

            placeholder.addWidget(new_strip)

    # ================================================================
    # HANDLE WINDOW RESIZE
    # ================================================================
    def resizeEvent(self, event):
        self.update_background()
        self.update_effect_gif()


# MAIN ENTRY
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = WeatherApp()
    w.show()
    sys.exit(app.exec())