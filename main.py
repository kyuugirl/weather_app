import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence
import requests
import pygame
import json
import os
import geocoder

g = geocoder.ip('me')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(BASE_DIR, "config.json")

def asset(path):
    return os.path.join(BASE_DIR, path)

# Load API key
with open(config_file, "r") as f:
    config = json.load(f)

API_key = config["key"]
city = g.city
base_url = "https://api.openweathermap.org/data/2.5/weather"

pygame.mixer.init()

class LofiWeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("The weather lounge")
        self.root.geometry("800x500")
        self.root.resizable(False, False)

        # Canvas for layering (background + animated snow)
        self.canvas = tk.Canvas(self.root, width=800, height=500, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.bg_img_id = None
        self.snow_frames = []
        self.snow_index = 0
        self.snow_id = None
        self.snow_active = False

        self.info_label = tk.Label(
            self.root,
            text="Loading weather...",
            font=("Courier New", 16),
            bg="#4777B5",
            fg="#cfd578"
        )
        self.info_label.place(relx=0.5, rely=0.1, anchor="center")

        self.update_weather()

    def get_weather(self, city):
        params = {"q": city, "appid": API_key, "units": "metric"}
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            messagebox.showerror("Error", f"Could not get weather for {city}")
            return None

    def update_weather(self):
        data = self.get_weather(city)
        if not data:
            return
        
        condition = data["weather"][0]["main"].lower()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].title()

        self.info_label.config(text=f"{city}: {desc}, {temp:.1f}°C")

        self.set_scene(condition)

    def set_scene(self, condition):
        # Reset animation 
        self.snow_active = False

        if "rain" in condition:
            bg = asset("assets/bgs/rain.jpg")
            music = asset("assets/music/rain.mp3")

        elif "snow" in condition:
            bg = asset("assets/bgs/snow.jpg")
            music = asset("assets/music/snow.mp3")
            snow = asset("assets/bgs/snow_anim.gif")
            self.load_snow_animation(snow)
            self.snow_active = True

        elif "clear" in condition:
            bg = asset("assets/bgs/clear.jpg")
            music = asset("assets/music/clear.mp3")

        else:
            bg = asset("assets/bgs/night.jpg")
            music = asset("assets/music/night.mp3")

        # Draw background
        bg_image = Image.open(bg).resize((800, 500))
        self.bg_photo = ImageTk.PhotoImage(bg_image)

        if self.bg_img_id is None:
            self.bg_img_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        else:
            self.canvas.itemconfig(self.bg_img_id, image=self.bg_photo)

        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)

        if self.snow_active:
            self.animate_snow()

    def load_snow_animation(self, gif_path):
        #Loads all gif frames so the animation can loop smoothly.
        self.snow_frames.clear()
        img = Image.open(gif_path)

        for frame in ImageSequence.Iterator(img):
            frame = frame.resize((800, 500))
            self.snow_frames.append(ImageTk.PhotoImage(frame))

        self.snow_index = 0

    def animate_snow(self):
        if not self.snow_active:
            return
        
        frame = self.snow_frames[self.snow_index]

        if self.snow_id is None:
            self.snow_id = self.canvas.create_image(0, 0, anchor="nw", image=frame)
        else:
            self.canvas.itemconfig(self.snow_id, image=frame)

        self.snow_index = (self.snow_index + 1) % len(self.snow_frames)

        self.root.after(80, self.animate_snow)  


if __name__ == "__main__":
    root = tk.Tk()
    app = LofiWeatherApp(root)
    root.mainloop()
