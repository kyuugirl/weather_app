import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import pygame
import json
import io
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(BASE_DIR, "config.json")

def asset(path):
    return os.path.join(BASE_DIR, path)

# Load config
with open(config_file, "r") as f:
    config = json.load(f)


API_key = config["key"]
city = config["city"]
base_url = "https://api.openweathermap.org/data/2.5/weather"

pygame.mixer.init()

class LofiWeatherApp:
    def __init__(self,root):
        self.root = root
        self.root.title("The weather lounge")
        self.root.geometry("800x500")
        self.root.resizable(False,False)

        self.bg_label = tk.Label(self.root)
        self.bg_label.pack(fill='both', expand=True )

        self.info_label = tk.Label(
            self.root,
            text="Loading weather...",
            font=("Courier New", 16),
            bg="#4777B5",
            fg="#cfd578"
        )
        self.info_label.place(relx=0.5,rely=0.1,anchor="center")

        self.update_weather()

    def get_weather(self, city):
        params= {"q": city, "appid": API_key, "units": "metric"}
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            messagebox.showerror("Error",f"could not get weather for{city}")
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
        if "rain" in condition:
            bg = asset("assets/bgs/rain.jpg")
            music = asset("assets/music/rain.mp3")
        elif "snow" in condition:
            bg = asset("assets/bgs/snow.jpg")
            music = asset("assets/music/snow.mp3")
        elif "clear" in condition:
            bg = asset("assets/bgs/clear.jpg")
            music = asset("assets/music/clear.mp3")
        else:
            bg = asset("assets/bgs/night.jpg")
            music = asset("assets/music/night.mp3")

        
        image = Image.open(bg)
        photo = ImageTk.PhotoImage(image)
        self.bg_label.configure(image=photo)
        self.bg_label.image = photo

        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)

if __name__ == "__main__":
    root = tk.Tk()
    app = LofiWeatherApp(root)
    root.mainloop()