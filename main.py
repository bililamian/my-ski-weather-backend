from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd

app = FastAPI(
    title="Ski Weather Backend API",
    description="Backend API for ski resort weather forecasting with elevation-based predictions"
)

# Resort data for Sunshine Village, Banff
RESORTS = {
    "sunshine_village": {
        "name": "Sunshine Village",
        "location": "Banff, Canada",
        "lat": 51.1164,
        "lon": -115.7631,
        "altitudes": {
            "top": 2730,    # meters
            "mid": 2200,
            "bot": 1660
        }
    }
}

# Pydantic models
class WeatherLayer(BaseModel):
    level: str
    altitude: int
    temperature: float
    precipitation: float
    condition: str
    icon: str

class ResortWeather(BaseModel):
    resort_name: str
    location: str
    timestamp: str
    layers: List[WeatherLayer]

def analyze_snow_condition(temp_c: float, precip_mm: float) -> tuple:
    """Analyze snow condition based on temperature and precipitation"""
    if precip_mm < 0.1:
        return "Cloudy/Clear", "☁️"
    
    if temp_c <= -12:
        return "Champagne Powder", "❄️💎"
    elif -12 < temp_c <= -3:
        return "Powder", "❄️"
    elif -3 < temp_c <= 0.5:
        return "Snow", "🌨️"
    elif 0.5 < temp_c <= 2.0:
        return "Wet Snow/Sleet", "💧❄️"
    else:
        return "Rain", "🌧️"

def generate_mock_weather_data(resort_id: str) -> List[Dict]:
    """Generate mock weather data for testing"""
    resort = RESORTS.get(resort_id)
    if not resort:
        return []
    
    # Mock data simulating a spring skiing scenario
    # Bot temperature gradually warming, crossing 0°C line
    periods = 5
    precip = [0.0, 2.5, 5.0, 1.5, 0.0]
    temps_bot = [-1.0, 0.0, 1.5, 2.5, 1.0]
    temps_mid = [-4.0, -3.0, -1.5, -0.5, -2.0]
    temps_top = [-8.0, -7.0, -5.5, -4.5, -6.0]
    
    base_time = datetime.utcnow()
    data = []
    
    for i in range(periods):
        timestamp = base_time + timedelta(hours=i * 3)
        
        for level, alt, temp in [
            ("Top", resort["altitudes"]["top"], temps_top[i]),
            ("Mid", resort["altitudes"]["mid"], temps_mid[i]),
            ("Bot", resort["altitudes"]["bot"], temps_bot[i])
        ]:
            condition, icon = analyze_snow_condition(temp, precip[i])
            data.append({
                "timestamp": timestamp.isoformat(),
                "level": level,
                "altitude": alt,
                "temperature": temp,
                "precipitation": precip[i],
                "condition": condition,
                "icon": icon
            })
    
    return data

@app.get("/")
def read_root():
    return {
        "message": "Ski Weather Backend API",
        "version": "1.0.0",
        "endpoints": [
            "/resorts - List all resorts",
            "/weather/{resort_id} - Get weather forecast for a resort"
        ]
    }

@app.get("/resorts")
def get_resorts():
    """Get list of all available resorts"""
    return {
        "resorts": [
            {
                "id": resort_id,
                "name": resort["name"],
                "location": resort["location"]
            }
            for resort_id, resort in RESORTS.items()
        ]
    }

@app.get("/weather/{resort_id}")
def get_weather(resort_id: str):
    """Get weather forecast for a specific resort"""
    resort = RESORTS.get(resort_id)
    if not resort:
        return {"error": "Resort not found"}
    
    weather_data = generate_mock_weather_data(resort_id)
    
    # Group by timestamp for easier consumption
    grouped_data = {}
    for entry in weather_data:
        ts = entry["timestamp"]
        if ts not in grouped_data:
            grouped_data[ts] = []
        grouped_data[ts].append(entry)
    
    return {
        "resort_name": resort["name"],
        "location": resort["location"],
        "coordinates": {
            "lat": resort["lat"],
            "lon": resort["lon"]
        },
        "forecasts": [
            {
                "timestamp": ts,
                "layers": layers
            }
            for ts, layers in grouped_data.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
