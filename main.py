import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk, ImageSequence
import pygame
import json
import os
import geocoder
from openWeatherMapAPI import OpenWeatherClient

# -------------------------------------------------------------
# UI CONSTANTS
# -------------------------------------------------------------
COLOR_BG = "#4777B5"
COLOR_TXT = "#cfd578"
COLOR_WEEKLY_TILE = "#5680A4"
FONT_MAIN = ("Courier New", 16)
FONT_HOURLY = ("Courier New", 14)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(BASE_DIR, "config.json")

def get_asset(path):
    return os.path.join(BASE_DIR, path)

# Load API key
with open(config_file, "r") as f:
    config = json.load(f)
API_key = config["key"]

pygame.mixer.init()

class LofiWeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("The weather lounge")
        self.root.geometry("800x500")
        self.root.resizable(False, False)

        # Detect user city based on IP
        g = geocoder.ip("me")
        self.city = g.city if g.city else "London"
        self.api = OpenWeatherClient(API_key, self.city)

        # Canvas = background + optional gif overlay
        self.canvas = tk.Canvas(self.root, width=800, height=500, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.bg_img_id = None
        self.current_music = None
        self.current_animation = None
        self.animation_frames = []
        self.animation_index = 0
        self.animation_id = None
        self.animation_active = False

        # Current weather label
        self.info_label = tk.Label(
            self.root,
            text="Loading weather...",
            font=FONT_MAIN,
            bg=COLOR_BG,
            fg=COLOR_TXT,
        )
        self.info_label.place(relx=0.5, rely=0.05, anchor="center")

        # Location dropdown + search
        self.city_var = tk.StringVar(value=self.city)
        self.dropdown = ttk.Combobox(self.root, textvariable=self.city_var, width=20)
        self.dropdown.place(relx=0.4, rely=0.12, anchor="center")
        self.search_btn = tk.Button(self.root, text="search", command=self.change_city)
        self.search_btn.place(relx=0.6, rely=0.12, anchor="center")

        # Weekly + hourly forecast containers
        self.weekly_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.weekly_frame.place(relx=0.5, rely=0.22, anchor="n")

        self.hourly_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.hourly_frame.place(relx=0.5, rely=0.50, anchor="n")

        self.update_weather()

    # -------------------------------------------------------------
    # Search / City change
    # -------------------------------------------------------------
    def change_city(self):
        new_city = self.city_var.get().strip()
        if not new_city:
            messagebox.showerror("Error", "City name empty, please enter a valid city")
            return

        # Query 2.5 Geo API for valid locations
        geo = self.api.session.get(
            self.api.geo_url,
            params={"q": new_city, "limit": 10, "appid": self.api.api_key},
        ).json()

        if not geo:
            messagebox.showerror("Error", "No matching locations found.")
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

        # Update dropdown list
        self.dropdown["values"] = cities

        # Select first city
        self.city = cities[0]

        # Set location coordinates
        self.api.lat = geo[0]["lat"]
        self.api.lon = geo[0]["lon"]

        self.update_weather()

    # -------------------------------------------------------------
    # Main Weather Update
    # -------------------------------------------------------------
    def update_weather(self):
        data = self.api.get_current_weather()

        condition = data["weather"][0]["main"].lower()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].title()
        desc = data["weather"][0]["description"].title()
        humidity = data["main"].get("humidity", "-")
        wind = data.get("wind", {}).get("speed", "-")

        # Top-center label
        current_text = (f"{self.city}:\n"f"{desc}"f", {temp:.1f}°C"f", Humidity:{humidity}%"f", Wind:{wind} m/s")
        self.info_label.config(text=current_text)

        # Update background and music
        self.set_scene(condition)

        # Cache daily forecast once
        self.daily_data = self.api.get_daily_forecast()

        # Draw weekly tiles
        self.show_weekly_forecast()

        # Default hourly = first day available
        first_day = list(self.daily_data.keys())[0]
        self.show_hourly_for_day(first_day)

    # -------------------------------------------------------------
    # WEEKLY FORECAST
    # -------------------------------------------------------------
    def show_weekly_forecast(self):
        for widget in self.weekly_frame.winfo_children():
            widget.destroy()

        for date, entries in self.daily_data.items():
            temps = [e["main"]["temp"] for e in entries]
            cond = entries[0]["weather"][0]["main"]

            btn = tk.Button(
                self.weekly_frame,
                text=f"{date}\n{min(temps):.0f}° / {max(temps):.0f}°\n{cond}",
                bg=COLOR_WEEKLY_TILE,
                fg="white",
                width=12,
                height=3,
                command=lambda d=date: self.show_hourly_for_day(d),
            )
            btn.pack(side="left", padx=5)

    # -------------------------------------------------------------
    # HOURLY FORECAST FOR ONE DAY
    # -------------------------------------------------------------
    def show_hourly_for_day(self, date):
        for widget in self.hourly_frame.winfo_children():
            widget.destroy()

        entries = self.daily_data[date]

        for e in entries:
            time = e["dt_txt"].split(" ")[1][:5]
            temp = e["main"]["temp"]
            cond = e["weather"][0]["main"]

            lbl = tk.Label(
                self.hourly_frame,
                text=f"{time}  {temp:.1f}°C  {cond}",
                font=FONT_HOURLY,
                bg=COLOR_BG,
                fg=COLOR_TXT,
            )
            lbl.pack(anchor="center")

    # -------------------------------------------------------------
    # BACKGROUND, MUSIC & SNOW EFFECTS
    # -------------------------------------------------------------
    def set_scene(self, condition):
        self.animation_active = False

        if "rain" in condition:
            bg = get_asset("assets/bgs/rainy.jpg")
            music = get_asset("assets/music/rain.mp3")

        elif "snow" in condition:
            bg = get_asset("assets/bgs/snow.jpg")
            music = get_asset("assets/music/snow.mp3")
            snow_gif = get_asset("assets/bgs/snow_anim.gif")
            self.load_animation(snow_gif)
            self.animation_active = True

        elif "clear" in condition:
            bg = get_asset("assets/bgs/sunny.jpg")
            music = get_asset("assets/music/sun.mp3")

        elif "cloud" in condition:
            bg = get_asset("assets/bgs/cloudy.jpg")
            music = get_asset("assets/music/cloudy.mp3")

        else:
            bg = get_asset("assets/bgs/night.jpg")
            music = get_asset("assets/music/night.mp3")

        # Background image
        bg_image = Image.open(bg).resize((800, 500))
        self.bg_photo = ImageTk.PhotoImage(bg_image)

        if self.bg_img_id is None:
            self.bg_img_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        else:
            self.canvas.itemconfig(self.bg_img_id, image=self.bg_photo)

        # Only reload music if different
        if music != self.current_music:
            pygame.mixer.music.load(music)
            pygame.mixer.music.play(-1)
            self.current_music = music

        if self.animation_active:
            self.animate()

    # -------------------------------------------------------------
    # SNOW GIF HANDLING
    # -------------------------------------------------------------
    def load_animation(self, gif_path):
        if self.current_animation == gif_path:
            return  # prevent reloading frames

        self.current_animation = gif_path
        self.animation_frames.clear()

        img = Image.open(gif_path)
        for frame in ImageSequence.Iterator(img):
            frame = frame.resize((800, 500))
            self.animation_frames.append(ImageTk.PhotoImage(frame))

        self.animation_index = 0

    def animate(self):
        if not self.animation_active:
            return

        frame = self.animation_frames[self.snow_index]

        if self.animation_id is None:
            self.animation_id = self.canvas.create_image(0, 0, anchor="nw", image=frame)
        else:
            self.canvas.itemconfig(self.animation_id, image=frame)

        self.snow_index = (self.animation_index + 1) % len(self.animation_frames)
        self.root.after(80, self.animate)

# -------------------------------------------------------------
# RUN APPLICATION
# -------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = LofiWeatherApp(root)
    root.mainloop()