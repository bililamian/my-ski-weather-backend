from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # [新增] 解决跨域问题

from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uvicorn

app = FastAPI(
    title="Ski Weather Backend API",
    description="Backend API for ski resort weather forecasting with elevation-based predictions",
    version="1.0.0"
)

# --- [新增] 配置 CORS ---
# 允许所有来源访问 (开发阶段为了方便)，防止 iOS 调试时报错
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resort data
RESORTS = {
    "sunshine_village": {
        "name": "Sunshine Village",
        "location": "Banff, Canada",
        "lat": 51.1164,
        "lon": -115.7631,
        "altitudes": {
            "top": 2730,
            "mid": 2200,
            "bot": 1660
        }
    }
}

# --- [修改] Pydantic models (匹配你的返回结构) ---

class WeatherLayer(BaseModel):
    level: str
    altitude: int
    temperature: float
    precipitation: float
    condition: str
    icon: str

class ForecastPoint(BaseModel):
    timestamp: str
    layers: List[WeatherLayer]

class ResortWeatherResponse(BaseModel):
    resort_name: str
    location: str
    coordinates: Dict[str, float]
    forecasts: List[ForecastPoint]  # 这里对应你代码里生成的 list

# --- 核心逻辑 ---

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
    resort = RESORTS.get(resort_id)
    if not resort:
        return []
    
    periods = 12  # [修改] 增加到 12 个时段，方便 iOS 测试滚动效果
    precip = [0.0, 2.5, 5.0, 1.5, 0.0, 0.0, 3.0, 6.0, 2.0, 0.0, 0.0, 0.0]
    
    # 简单的温度模拟逻辑
    base_temps_bot = [-1.0, 0.0, 1.5, 2.5, 1.0, -2.0, -3.0, -1.0, 0.5, 1.0, -1.0, -2.0]
    
    base_time = datetime.utcnow()
    data = []
    
    for i in range(periods):
        timestamp = base_time + timedelta(hours=i * 3)
        
        # 简单的直减率模拟：每上升1000米，降温约6.5度
        t_bot = base_temps_bot[i] if i < len(base_temps_bot) else 0.0
        t_mid = t_bot - ((resort["altitudes"]["mid"] - resort["altitudes"]["bot"]) / 1000 * 6.5)
        t_top = t_bot - ((resort["altitudes"]["top"] - resort["altitudes"]["bot"]) / 1000 * 6.5)
        
        # 确保 precip 列表够长
        p_val = precip[i] if i < len(precip) else 0.0
        
        for level, alt, temp in [
            ("Top", resort["altitudes"]["top"], round(t_top, 1)),
            ("Mid", resort["altitudes"]["mid"], round(t_mid, 1)),
            ("Bot", resort["altitudes"]["bot"], round(t_bot, 1))
        ]:
            condition, icon = analyze_snow_condition(temp, p_val)
            data.append({
                "timestamp": timestamp.isoformat(),
                "level": level,
                "altitude": alt,
                "temperature": temp,
                "precipitation": p_val,
                "condition": condition,
                "icon": icon
            })
    
    return data

# --- Endpoints ---

@app.get("/")
def read_root():
    return {
        "message": "Ski Weather Backend API",
        "status": "running",
        "docs_url": "http://127.0.0.1:8000/docs"
    }

@app.get("/resorts")
def get_resorts():
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

# [修改] 增加 response_model，这样 FastAPI 会自动校验返回数据格式，且文档更清晰
@app.get("/weather/{resort_id}", response_model=ResortWeatherResponse)
def get_weather(resort_id: str):
    resort = RESORTS.get(resort_id)
    if not resort:
        raise HTTPException(status_code=404, detail="Resort not found")  # 使用标准异常
    
    weather_data = generate_mock_weather_data(resort_id)
    
    # Group by timestamp
    grouped_data = {}
    for entry in weather_data:
        ts = entry["timestamp"]
        if ts not in grouped_data:
            grouped_data[ts] = []
        # 从 entry 中移除 timestamp 字段，因为它已经在父级了 (可选，为了数据整洁)
        layer_entry = entry.copy()
        del layer_entry["timestamp"]
        grouped_data[ts].append(layer_entry)
    
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
