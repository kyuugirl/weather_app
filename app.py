import os
import sys
import json
import pygame
import geocoder
from openWeatherMapAPI import OpenWeatherClient
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QStackedLayout, QVBoxLayout
from PyQt6.QtGui import QGuiApplication, QFont, QPixmap, QPainter, QMovie

# -------------------------------------------------------------
# UI CONSTANTS
# -------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(BASE_DIR, "config.json")

def get_asset(path):
    return os.path.join(BASE_DIR, "assets/", path)

# Load API key
with open(config_file, "r") as f:
    config = json.load(f)
API_key = config["key"]

class LofiWeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The weather lounge")
        self.setFixedSize(375,375)
        self.move_to_top_right()

        # Start audio engine
        pygame.mixer.init()

        # 2 main layouts: Not sure which looks better, so stacking both for now
        self.layout = QStackedLayout()
        self.setLayout(self.layout)

        # Initialize Current Background 
        self.background = QPixmap()

        # animated foreground GIF
        self.gif_label = QLabel(self)
        self.gif_label.setGeometry(0, 0, 375, 375)   # full window or custom area
        self.gif_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.movie = QMovie(get_asset("effects/rain.gif"))
        self.gif_label.setMovie(self.movie)
        self.movie.start()


    # Place window at top-right corner of the screen
    def move_to_top_right(self):
        screen = QGuiApplication.primaryScreen()
        geo = screen.availableGeometry()
        x = geo.width() - self.width()
        y = 0
        self.move(x, y)

    def update_background(self, path):
        self.background = QPixmap(path)
        self.update()   # trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.background.isNull():
            painter.drawPixmap(self.rect(), self.background)


# -------------------------------------------------------------
# RUN APPLICATION
# -------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LofiWeatherApp()
    window.show()
    sys.exit(app.exec())