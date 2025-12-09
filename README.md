**Weather-Lofi Desktop Widget**
A lightweight Python application that displays real-time weather conditions and plays a matching lofi track. It uses the OpenWeather API to provide current conditions, a weekly forecast, and expandable hourly data for individual days. You can also select the location you want to monitor.

# Overview
This project combines weather data with ambient audio to create a calm, informative desktop widget. The goal is to offer a quick scientific snapshot of atmospheric conditions without overwhelming detail.

Key ideas are simple:
1. Read current weather from OpenWeather
2. Match the condition group (clear, clouds, rain, etc.) with a lofi track
3. Show the week’s weather in a compact layout
4. Expand any day to view hourly changes
5. Allow the user to choose a location anywhere in the world

# Weather System
This widget uses the OpenWeather API to gather atmospheric data and classify conditions into simple groups. Each group controls the visual theme and selects a matching lofi track.

## Condition Groups
OpenWeather codes are translated into broad, easy-to-understand categories:

**Group	            Meaning**
Thunderstorm	    Electrical storms with varying rainfall
Drizzle	            Light precipitation with small droplets
Rain	            Steady or heavy precipitation
Snow	            Frozen precipitation, snow or sleet
Atmosphere	        Mist, fog, haze, dust, or smoke
Clear	            No cloud cover
Clouds	            Light, scattered, broken, or overcast clouds

More on weather conditions: https://openweathermap.org/weather-conditions
2 = thunder, 3 = drizzle, 5 = rain, 6 = snow, 7 = fog/dust, 8 = clear/clouds.

## Forecast Display
- The main screen shows the current weather conditions
- The weekly panel provides 5 days of compact summaries
- Expanded table reveals 3 hour interval of the day's forcast with temperature and precipitation trends

# Features
## Current Weather
- Temperature, general condition, description
- Condition classification based on OpenWeather codes
- Auto-selected lofi track and image that fits the current atmosphere

## Weekly Forecast
- five-day summary with temperature and condition icons
- Scientific values kept simple: max/min temperature and general condition
- Click any day to reveal hourly data

## Hourly Weather Details
- Temperature
- Precipitation probability
- General condition (small icons/gifs)

## Location Selection
- Search for any location
- Use current location on start up based on IP Address

Refreshes the widget automatically after a given time 

# How It Works
1. The program requests weather data from OpenWeather’s Current Weather and Forecast endpoints.
2. Weather codes are grouped (e.g., 2xx = thunderstorm, 3xx = drizzle).
3. These groups map to predefined audio playlists.
4. A compact GUI displays the current snapshot and upcoming days.

To easily remember the architecture: API → Filter → Match → Display → Audio.

# Requirements
- Python 3.9+_
- OpenWeather API key

## Required external packages
- pyqt6, json, os → built into Python
- Pillow → needed for PIL
- requests → HTTP calls to OpenWeather
- pygame → audio playback for lofi
- geocoder → geolocation lookup

**Footnote**  
- While the application is running, use **CTRL+M** to toggle music on or off.
- Music files are not included due to size constraints.  
- If using the source code, replace the placeholder API key in 'config.json' with your own.  
- The file `openWeatherMapAPI.py` contains commented code for API 3.0, which can be enabled if you have the appropriate key.
  



