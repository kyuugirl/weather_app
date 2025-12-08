from collections import Counter
import os
import sys
import json
import pygame
import geocoder
import random
from PyQt6.QtGui import QKeySequence, QShortcut
from datetime import datetime, timedelta, timezone
from openWeatherMapAPI import OpenWeatherClient
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QStackedLayout, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QSizePolicy, QGridLayout, QScrollArea
from PyQt6.QtGui import QGuiApplication, QFont, QPixmap, QPainter, QMovie, QIcon
from PyQt6.QtCore import Qt, QSize, QTimer

# -------------------------------------------------------------
# PATH HELPERS
# -------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(BASE_DIR, "config.json")

def get_asset(path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, "assets", path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),"assets", path)

# Load API key
with open(config_file, "r") as f:
    config = json.load(f)
API_Key = config["key"]


# Mapping icons to GIFs
ICON_MAP = {
    "01d": get_asset("icons/clear_d.gif"),
    "01n": get_asset("icons/clear_n.gif"),
    "02d": get_asset("icons/few_clouds_d.gif"),
    "02n": get_asset("icons/few_clouds_n.gif"),
    "03d": get_asset("icons/scattered_clouds.gif"),
    "03n": get_asset("icons/scattered_clouds.gif"),
    "04d": get_asset("icons/broken_clouds.gif"),
    "04n": get_asset("icons/broken_clouds.gif"),
    "09d": get_asset("icons/rain.gif"),
    "09n": get_asset("icons/rain.gif"),
    "10d": get_asset("icons/rain.gif"),
    "10n": get_asset("icons/rain.gif"),
    "11d": get_asset("icons/storm.gif"),
    "11n": get_asset("icons/storm.gif"),
    "13d": get_asset("icons/snow.gif"),
    "13n": get_asset("icons/snow.gif"),
    "50d": get_asset("icons/fog.gif"),
    "50n": get_asset("icons/fog.gif"),
}

# same as icon cept for music 
MUSIC_MAP = {
    "clear": [
        get_asset("music/clear1.mp3"),
        get_asset("music/clear2.mp3"),
        get_asset("music/clear3.mp3"),
        get_asset("music/clear4.mp3"),
    ],
    "clouds": [
        get_asset("music/clouds1.mp3"),
        get_asset("music/clouds2.mp3"),
        get_asset("music/clouds3.mp3"),
        get_asset("music/clouds4.mp3"),
    ],
    "rain": [
        get_asset("music/rain1.mp3"),
        get_asset("music/rain2.mp3"),
        get_asset("music/rain3.mp3"),
        get_asset("music/rain4.mp3"),
    ],
    "drizzle": [
        get_asset("music/drizzle1.mp3"),
        get_asset("music/drizzle2.mp3"),
        get_asset("music/drizzle3.mp3"),
        get_asset("music/drizzle4.mp3"),
    ],
    "thunderstorm": [
        get_asset("music/thunder1.mp3"),
        get_asset("music/thunder2.mp3"),
        get_asset("music/thunder3.mp3"),
        get_asset("music/thunder4.mp3"),
    ],
    "snow": [
        get_asset("music/snow1.mp3"),
        get_asset("music/snow2.mp3"),
        get_asset("music/snow3.mp3"),
        get_asset("music/snow4.mp3"),
    ],
    "squall": [
        get_asset("music/squall1.mp3"),
        get_asset("music/squall2.mp3"),
        get_asset("music/squall3.mp3"),
        get_asset("music/squall4.mp3"),

    ],
    "atmosphere": [
        get_asset("music/atmo1.mp3"),
        get_asset("music/atmo2.mp3"),
        get_asset("music/atmo3.mp3"),
        get_asset("music/atmo4.mp3"),
    ],

}
# -------------------------------------------------------------
# METRIC WIDGET
# -------------------------------------------------------------
class MetricWidget(QWidget):
    def __init__(self, icon_path, value_text, label_text, parent=None):
        super().__init__(parent)

        # Transparent background so it blends with your animated UI
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowMinMaxButtonsHint
        )

        self.setStyleSheet("""

            QMainWindow {
                background: transparent;                   
            }
        """)

        # ---------- MAIN HORIZONTAL LAYOUT ----------
        hbox = QHBoxLayout(self)
        hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        hbox.setSpacing(6)
        hbox.setContentsMargins(0, 0, 0, 0)

        # ---------- ICON ----------
        self.icon_label = QLabel(self)
        pix = QPixmap(icon_path).scaled(
            28, 28,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.icon_label.setPixmap(pix)
        self.icon_label.setStyleSheet("background: transparent;")

        # ---------- RIGHT SIDE (VALUE + LABEL) ----------
        right_box = QWidget(self)
        vbox = QVBoxLayout(right_box)
        vbox.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        # VALUE (bold)
        self.value_label = QLabel(value_text)
        self.value_label.setStyleSheet("""
            color: white;
            font-size: 10px;
            font-weight: bold;
            background: transparent;
        """)

        # LABEL (small text)
        self.text_label = QLabel(label_text)
        self.text_label.setStyleSheet("""
            color: white;
            font-size: 10px;
            font-weight: bold;
            background: transparent;
        """)

        # Add to vertical layout
        vbox.addWidget(self.value_label, alignment=Qt.AlignmentFlag.AlignLeft)
        vbox.addWidget(self.text_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Add icon + right column to horizontal layout
        hbox.addWidget(self.icon_label)
        hbox.addWidget(right_box)

        self.setStyleSheet("""
            background: rgba(100,100,100,40);
            border: 1px solid rgba(200,200,200,70);
            border-radius: 10px;
            padding: 4px;                   
        """)

    # Public update text
    def set_value(self, text):
        self.value_label.setText(text)

# Clickable widget base class
class ClickableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicked = None  # callback function

    def mousePressEvent(self, event):
        if self.clicked:
            self.clicked()
        super().mousePressEvent(event)


# -------------------------------------------------------------
# MAIN APP
# -------------------------------------------------------------
class LofiWeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The weather lounge")
        self.resize(450,450)
        self.move_to_top_right()

        # Start audio engine
        pygame.mixer.init()

        # IMPORTANT: central widget for layouts
        glass = QWidget(self)
        glass.setStyleSheet("""
            background: rgba(100,100,100,40);
            border: 1px solid rgba(200,200,200,80);
            border-radius: 20px;
            backdrop-filter: blur(30px);  
        """)
        
        self.central = glass
        self.setCentralWidget(glass)

        # VBox main layout
        self.main_layout = QVBoxLayout(glass)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)

        # Background + foreground animation + music
        self.background = QPixmap()
        self.movie = None
        self.music = None

        # Detect user city based on IP
        geolocation = geocoder.ip("me")
        location = geolocation.city if geolocation.city else "London"

        # Connect to OpenWeatherMap API
        self.api = OpenWeatherClient(API_Key, location)
        
        # Dropdown search box at top-left
        self.location_dropdown = QComboBox(self)
        self.location_dropdown.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.location_dropdown.setEditable(True)
        self.location_dropdown.setEditText(self.api.city)
        self.location_dropdown.setFixedWidth(300)
        self.location_dropdown.setContentsMargins(0, 0, 0, 0)

        # Background + foreground animation
        line_edit = self.location_dropdown.lineEdit()
        line_edit.addAction(
            QIcon(get_asset("icons/location_pin.png")),
            line_edit.ActionPosition.LeadingPosition
        )
        
        # Styling
        self.location_dropdown.setStyleSheet("""
            QComboBox {
                color: white;
                background: rgba(200,200,200,40); 
                padding: 6px 10px;
                border-radius: 12px;
                border: 2px solid rgba(200,200,200,120);
                font-size: 15px;
                font-weight: bold;
                backdrop-filter: blur(25px);
                                        
            }
            QComboBox: hover{
                background: rgba(255,255,255,80);
            }                              
                                                
            QComboBox QAbstractItemView {
                background: rgba(30,30,30,150);
                color: white;
                border: 1px solid rgba(255,255,255,50);
            }
        """)
        
        # ENTER triggers searching
        self.location_dropdown.lineEdit().returnPressed.connect(self.list_cities)
        
        # USER SELECTS from dropdown → update weather
        self.location_dropdown.activated.connect(self.select_city)

        # Store last lookup results
        self._last_geo_results = None

        # Stacked layout inside main layout
        self.layout_stack = QStackedLayout()
        self.main_layout.addWidget(self.location_dropdown) 
        self.main_layout.addLayout(self.layout_stack)   

        # Create UI Layouts
        screen1 = self.layout_one()
        self.layout_stack.addWidget(screen1)

        self.update_weather()

        # Auto-update weather every hour (3600000 ms)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_weather)
        self.update_timer.start(3600000)  # 1 hour in milliseconds

        mute = QShortcut(QKeySequence("Ctrl+M"), self)
        mute.activated.connect(self.toggle_music)



    # Place window at top-right corner of the screen
    def move_to_top_right(self):
        screen = QGuiApplication.primaryScreen()
        geo = screen.availableGeometry()
        self.move(geo.width() - self.width(), 0)

    def update_background(self, path):
        self.background = QPixmap(path)
        self.update()

    def update_foreground(self, path):
        if self.movie:
            self.movie.stop()
        self.movie = QMovie(path)
        self.movie.frameChanged.connect(self.repaint)
        self.movie.start()

    def paintEvent(self, event):
        painter = QPainter(self)

        # draw background
        if not self.background.isNull():
            painter.drawPixmap(self.rect(), self.background)

        # draw foreground frame (GIF)
        if self.movie:
            frame = self.movie.currentPixmap()
            if not frame.isNull():
                scaled = frame.scaled(self.rect().size(), 
                                    Qt.AspectRatioMode.IgnoreAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)
                painter.drawPixmap(0, 0, scaled)
    
    # City Dropdown Search
    def list_cities(self):
        city = self.location_dropdown.currentText().strip()
        if not city:
            QMessageBox.information(self, "Error", "City name empty, please enter a valid city")
            return

        # Query the 2.5 API to check if location is valid
        geo = self.api.session.get(self.api.geo_url, params = {"q": city, "limit": 10, "appid": API_Key},).json()
        if not geo:
            QMessageBox.information(self, "Error", "No matching locations found.")
            return

        # Build formatted dropdown list
        cities = []
        for g in geo:
            name = g.get("name", "")
            country = g.get("country", "")
            state = g.get("state", "")

            if state:
                display = f"{name}, {state}, {country}"
            else:
                display = f"{name}, {country}"

            cities.append(display)

        # Store results for later selection
        self._last_geo_results = geo

        # Update dropdown list but keep user input
        typed = city
        self.location_dropdown.blockSignals(True)
        self.location_dropdown.clear()
        self.location_dropdown.addItems(cities)
        self.location_dropdown.setEditText(typed)
        self.location_dropdown.blockSignals(False)

        # Open the list so user chooses an option
        self.location_dropdown.showPopup()

    def select_city(self, index):
        if not self._last_geo_results:
            return

        geo = self._last_geo_results[index]
        self.api.lat = geo["lat"]
        self.api.lon = geo["lon"]
        self.api.city = self.location_dropdown.currentText()

        self.update_weather()

    # Layout one
    def layout_one(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(5)

        # Date label
        self.date_label_1 = QLabel("")
        font = QFont("Arial", 18)
        font.setBold(True)
        self.date_label_1.setFont(font)
        self.date_label_1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.date_label_1.setStyleSheet("color: white;")

        # Temp label
        self.temp_label_1 = QLabel("0°C")
        font2 = QFont("Arial", 24)
        font2.setBold(True)
        self.temp_label_1.setFont(font2)
        self.temp_label_1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.temp_label_1.setStyleSheet("color: white;")

        # Condition label
        self.condition_label_1 = QLabel("Condition")
        font3 = QFont("Arial", 14)
        self.condition_label_1.setFont(font3)
        self.condition_label_1.setStyleSheet("color: white;")

        # Metrics container
        metric_container = QWidget() 
        metric_container.setStyleSheet("background: transparent;")
        
        main_hbox = QHBoxLayout(metric_container)
        main_hbox.setContentsMargins(0, 0, 0, 0)
        main_hbox.setSpacing(0)
        main_hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.humidity_widget_1 = MetricWidget(get_asset("icons/humidity.png"), "0%", "Humidity")
        self.wind_widget_1 = MetricWidget(get_asset("icons/wind.png"), "0 m/s", "Wind Speed")

        main_hbox.addWidget(self.humidity_widget_1, alignment=Qt.AlignmentFlag.AlignLeft)
        main_hbox.addWidget(self.wind_widget_1, alignment=Qt.AlignmentFlag.AlignLeft)

        # Add everything to vertical layout
        layout.addWidget(self.date_label_1)
        layout.addWidget(self.temp_label_1)
        layout.addWidget(self.condition_label_1)
        layout.addWidget(metric_container, stretch=0)

        metric_container.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        # Draw weekly tiles
        self.forcast = self.build_weekly_table()
        layout.addWidget(self.forcast)        

        # Draw hourly panel for first day
        self.hourly_panel = self.build_hourly_panel()        
        layout.addWidget(self.hourly_panel)

        # Add stretch to push UI to top
        layout.addStretch()

        return container
    
    # WEEKLY FORECAST
    def build_weekly_table(self):
        wrapper = QWidget()
        wrapper.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.week_grid = QGridLayout(wrapper)
        self.week_grid.setSpacing(5)
        self.week_grid.setContentsMargins(0, 0, 0, 0)

        # Store day tiles for later update
        self.weekly_tiles = []

        for i in range(8):
            # Labels for day / icon / min-max temp
            day_lbl = QLabel("")
            day_lbl.setStyleSheet("color:white; font-size:12px; font-weight:bold;")
            day_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            cond_icon = QLabel()
            cond_icon.setFixedSize(48, 48)
            cond_icon.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            temp_lbl = QLabel("")
            temp_lbl.setStyleSheet("color:white; font-size:12px;")
            temp_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Store references for updating
            tile = {
                "block": ClickableWidget(),
                "day": day_lbl,
                "icon": cond_icon,
                "temp": temp_lbl,
                "movie": None,
                "date_key": None
            }

            tile["block"].setStyleSheet("""
                background: rgba(100,100,100,70);
                border: 1px solid rgba(255, 255, 255,100);
                border-radius: 14px;
                padding: 6px;
                backdrop-filter: blur(20px);                            
            
            """)

            # ----- Vertical block for the day -----
            v = QVBoxLayout(tile["block"])
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.addWidget(day_lbl)
            v.addWidget(cond_icon)
            v.addWidget(temp_lbl)

            self.week_grid.addWidget(tile["block"], 0, i)
            self.weekly_tiles.append(tile)

            # clickable callback assigned later in update
            tile["block"].clicked = lambda: None
        
        return wrapper

    # Update weekly tiles with data
    def update_weekly_table(self):
        days = list(self.daily_data.items())[:8]

        for i, (date_key, entries) in enumerate(days):
            tile = self.weekly_tiles[i]

            # Update date key and day label
            tile["date_key"] = date_key
            d = datetime.strptime(date_key, "%Y-%m-%d")
            tile["day"].setText(d.strftime("%a"))
           
            # Most Common Weather Condition icon selection
            icons = [e["weather"][0]["icon"] for e in entries]
            icon_code = Counter(icons).most_common(1)[0][0]
            gif_path = ICON_MAP.get(icon_code, get_asset("icons/clear_d.gif"))

            movie = QMovie(gif_path)
            movie.setScaledSize(tile["icon"].size())
            tile["icon"].setMovie(movie)
            movie.start()
            tile["movie"] = movie

            # Min/Max Temps
            temps = [e["main"]["temp"] for e in entries]
            min_temp = min(temps)
            max_temp = max(temps)
            tile["temp"].setText(f"{min_temp:.0f}°C / {max_temp:.0f}°C")

            # Clickable callback to update hourly panel
            tile["block"].clicked = lambda key=date_key: self.update_hourly_panel(key)
        
        # Hide unused tiles (if less than 6 days)
        for j in range(i + 1, len(self.weekly_tiles)):
            self.weekly_tiles[j]["block"].hide()
            
    # Hourly forecast panel
    def build_hourly_panel(self):
        # Scroll area for hourly entries
        self.hourly_scroll = QScrollArea()
        self.hourly_scroll.setWidgetResizable(True)
        self.hourly_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.hourly_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.hourly_scroll.setStyleSheet("background: transparent; border: none;")

        self.hourly_container = QWidget()
        self.hourly_layout = QVBoxLayout(self.hourly_container)
        self.hourly_layout.setContentsMargins(0, 0, 0, 0)
        self.hourly_layout.setSpacing(0)

        self.hourly_scroll.setWidget(self.hourly_container)
        self.hourly_scroll.setStyleSheet("""
        QScrollArea {
            background: transparent;
            border: none;
        }
        QWidget {
            background: rgba(100,100,100,70);
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,80);
            backdrop-filter: blur(20px);                                 
        }                         
        """)

        # pre-create row widgets (max 24 entries)
        self.hour_rows = []
        self.max_rows = 24

        for i in range(self.max_rows):
            # Hourly entry row
            row = QWidget()
            grid = QGridLayout(row)
            grid.setContentsMargins(0, 0, 0, 0) 
            grid.setHorizontalSpacing(0)          
            grid.setVerticalSpacing(0) 

            # Labels for time / icon / humidity / temp
            hour_lbl = QLabel("")
            hour_lbl.setStyleSheet("color:white; font-size:13px; font-weight:bold;")

            cond_icon = QLabel()
            cond_icon.setFixedSize(40, 40)

            humidity_lbl = QLabel("")
            humidity_lbl.setStyleSheet("color:white; font-size:13px;")

            temp_lbl = QLabel("")
            temp_lbl.setStyleSheet("color:white; font-size:14px; font-weight:bold;")

            # Equal column weighting
            grid.setColumnStretch(0, 1)  # time
            grid.setColumnStretch(1, 1)  # icon
            grid.setColumnStretch(2, 1)  # humidity
            grid.setColumnStretch(3, 1)  # temp

            grid.addWidget(hour_lbl,     0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
            grid.addWidget(cond_icon,    0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(humidity_lbl, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(temp_lbl,     0, 3, alignment=Qt.AlignmentFlag.AlignRight)

            self.hourly_layout.addWidget(row)

            # Store references so we can update them later
            self.hour_rows.append({
                "row": row,
                "hour": hour_lbl,
                "icon": cond_icon,
                "humidity": humidity_lbl,
                "temp": temp_lbl,
                "movie": None,
            })

        self.hourly_layout.addStretch()
        return self.hourly_scroll

    # Update hourly panel for a given day
    def update_hourly_panel(self, date):
        hourly = self.daily_data[date]

        for i, entry in enumerate(hourly):
            row = self.hour_rows[i]

            # Time range
            dt = datetime.fromtimestamp(entry["dt"], timezone.utc)
            dt_end = dt + timedelta(hours=3)
            hour_start = dt.strftime("%H:%M")
            hour_end   = dt_end.strftime("%H:%M")
            row["hour"].setText(f"{hour_start} - {hour_end}")

            # Icon (GIF)
            icon_code = entry["weather"][0]["icon"]
            gif_path = ICON_MAP.get(icon_code, get_asset("icons/clear_d.gif"))

            movie = QMovie(gif_path)
            movie.setScaledSize(row["icon"].size())
            row["icon"].setMovie(movie)
            movie.start()
            row["movie"] = movie

            # Humidity
            row["humidity"].setText(f"{entry['main']['humidity']}%")

            # Temperature
            row["temp"].setText(f"{entry['main']['temp']:.0f}°C")                       

            row["row"].show()

            # Hide unused rows
            for j in range(len(hourly), self.max_rows):
                self.hour_rows[j]["row"].hide()
        
    def update_weather(self):
        data = self.api.get_current_weather()

        dt = datetime.fromtimestamp(data["dt"], timezone.utc)
        date_str = dt.strftime("%A - %B %d")
        temp = data["main"]["temp"]
        condition = data["weather"][0]["main"].lower()
        icon = data["weather"][0]["icon"]
        desc = data["weather"][0]["description"].title()
        humidity = data["main"].get("humidity", "-")
        wind = data.get("wind", {}).get("speed", "-")

        # Date label
        self.date_label_1.setText(f"{date_str}")
        # Temp label
        self.temp_label_1.setText(f"{temp:.1f}°C")
        # Condition label
        self.condition_label_1.setText(f"{desc}")
        # Metrics
        self.humidity_widget_1.set_value(f"{humidity}%")
        self.wind_widget_1.set_value(f"{wind}m/s")
        
        # Update background and music
        self.set_scene(condition, icon)

        # Cache daily forecast
        self.daily_data = self.api.get_daily_forecast()

        # Update weekly weather table and hourly panel
        self.update_weekly_table()

        # Default hourly = first day available
        first_day = list(self.daily_data.keys())[0]
        self.update_hourly_panel(first_day)

    # Select background, forground and music based on condition
    def set_scene(self, condition, icon):
        condition = condition.lower()
        is_night = icon.endswith("n")
        dn = "n" if is_night else "d"

        # Default values
        fg_path = None
        music_path = get_asset("music/clear1.mp3")

        # Special mapping for background filenames
        condition_map = {
            "clear": "clear",
            "clouds": "clouds",
            "rain": "rain",
            "drizzle": "drizzle",
            "thunderstorm": "thunderstorm",
            "snow": "snow",
            "mist": "fog",
            "fog": "fog",
            "haze": "fog",
            "smoke": "smoke",
            "dust": "dust",
            "sand": "dust",
            "ash":  "smoke",
            "squall": "squall",
            "tornado": "tornado"
        }

        # Pick background root name based on condition category
        root = condition_map.get(condition, "clear")

        # Background path (day/night aware)
        bg_path = get_asset(f"backgrounds/{root}_{dn}.jpg")

        music_key = None

        # Foreground effects
        if condition in ["rain", "drizzle"]:
            fg_path = get_asset("effects/rain.gif")  
            music_key = "rain" if condition == "rain" else "drizzle" 

        elif condition == "thunderstorm":
            fg_path = get_asset("effects/thunder.gif") 
            music_key = "thunderstorm"

        elif condition == "snow":
            fg_path = get_asset("effects/snow.gif")
            music_key = "snow"

        elif condition == "squall":
            fg_path = get_asset("effects/squall.gif")
            music_key = "squall"

        # Fog/haze/etc share no foreground (currently)
        elif condition in ["mist", "fog", "haze",]:
            fg_path = get_asset("effects/fog.gif")
            music_key = "atmosphere"

        elif condition in ["smoke", "dust", "ash", "sand"]:
            fg_path = get_asset("effects/dust.gif")
            music_key = "atmosphere"

        else:
            if condition == "clouds":
                music_key = "clouds"
            else:
                music_key = "clear"

        if music_key is not None and music_key in MUSIC_MAP:
            music_path = random.choice(MUSIC_MAP[music_key])

        # Update UI
        self.update_background(bg_path)
        self.update_foreground(fg_path)

        # Music playback
        if getattr(self, "music", None) != music_path:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)
            self.music = music_path

    def toggle_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
    

# -------------------------------------------------------------
# RUN APPLICATION
# -------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LofiWeatherApp()
    window.show()
    sys.exit(app.exec())