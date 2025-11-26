import requests

class OpenWeatherClient:

    def __init__(self, api_key, city):
        self.api_key = api_key
        self.geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        # 2.5 Endpoint urls
        self.current_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        # 3.0 Endpoint url
        # self.onecall_url = "https://api.openweathermap.org/data/3.0/onecall"
        self.session = requests.Session()
        self.set_location(city)

    def set_location(self, city):
        params = {
            "q": city,
            "limit": 1,
            "appid": self.api_key
        }
        responce = self.session.get(self.geo_url, params=params)
        responce.raise_for_status()
        data = responce.json()
        if not data:
            raise ValueError(f"City '{city}' not found.")
        self.lat, self.lon = data[0]["lat"], data[0]["lon"]

    # Get current weather at a preset location
    def get_current_weather(self):
        params = {
            "lat": self.lat,
            "lon": self.lon,
            "appid": self.api_key,
            "units": "metric"
        }
        res = self.session.get(self.current_url, params=params)
        res.raise_for_status()
        return res.json()
    
    # Get 3-hourly forecast
    def get_hourly_forecast(self):
        params = {
            "lat": self.lat,
            "lon": self.lon,
            "appid": self.api_key,
            "units": "metric"
        }
        r = self.session.get(self.forecast_url, params=params)
        r.raise_for_status()
        return r.json()["list"]   # 3-hour steps

    # Daily forcast not available, derive it from 3-hour forcast
    def get_daily_forecast(self):
        hourly = self.get_hourly_forecast()
        daily = {}
        for entry in hourly:
            date = entry["dt_txt"].split(" ")[0]
            daily.setdefault(date, []).append(entry)
        
        return daily

    # Bundle everything in one go
    def get_all_weather(self):
        return {
            "current": self.get_current_weather(),
            "hourly": self.get_hourly_forecast(),
            "daily": self.get_daily_forecast()
        }

# -------------------------------------------------------------
# Methods for open weather map api with access to 3.0 
# -------------------------------------------------------------
    # # Helper function make a request to openweathermap API.
    # def request(self, exclude=None):
    #     params = {
    #         "lat": self.lat,
    #         "lon": self.lon,
    #         "appid": self.api_key,
    #         "units": "metric"
    #     }
    #     if exclude:
    #         params["exclude"] = exclude

    #     r = self.session.get(self.onecall_url, params=params)
    #     r.raise_for_status()
    #     return r.json()
    
    # # Get current weather at a preset location
    # def get_current_weather(self):
    #     data = self.request(exclude="minutely,current,daily,alerts")
    #     return data["current"]

    # # Get the next 48h weather forcast at a preset location
    # def get_hourly_forecast(self):
    #     data = self.request(exclude="minutely,current,daily,alerts")
    #     return data["hourly"]
    
    # # Get the weekly forcast at a preset location
    # def get_weekly_forecast(self):
    #     data = self.request(exclude="minutely,current,hourly,alerts")
    #     return data["daily"]
    
    # # Return current, hourly, and daily weather in one call
    # def get_all_weather(self):
    #     data = self.request()  # no exclusions → full dataset

    #     return {
    #         "current": data.get("current"),
    #         "hourly": data.get("hourly"),
    #         "daily": data.get("daily")
    #     }