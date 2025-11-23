# my-ski-weather-backend
Backend API for ski resort weather forecasting with elevation-based predictions (FastAPI)


## Overview

This is a FastAPI-based backend service that provides weather forecasts for ski resorts with elevation-based predictions. The API returns weather data for three elevation levels (Top, Mid, Bot) and includes intelligent snow condition analysis.

Inspired by Snow-Forecast.com, this project aims to help skiers and snowboarders plan their trips by showing different weather conditions at different elevations on the mountain.

## Features

- ⛷️ **Multi-Level Weather Forecasts**: Get weather predictions for Top, Mid, and Bottom elevations
- ❄️ **Snow Condition Analysis**: Intelligent algorithm determines snow quality (Powder, Wet Snow, Rain, etc.)
- 🏔️ **Sunshine Village Data**: Currently includes mock data for Sunshine Village, Banff, Canada
- 🔄 **RESTful API**: Easy-to-use JSON API endpoints
- 🚀 **FastAPI**: Built with modern async Python framework

## Resort Data

**Sunshine Village, Banff**
- Top: 2730m
- Mid: 2200m  
- Bot: 1660m
- Location: 51.1164°N, 115.7631°W

## API Endpoints

### Get Root Info
```
GET /
```
Returns API information and available endpoints.

### List All Resorts
```
GET /resorts
```
Returns a list of all available ski resorts.

### Get Weather Forecast
```
GET /weather/{resort_id}
```
Returns detailed weather forecast for a specific resort.

Example:
```
GET /weather/sunshine_village
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/bililamian/my-ski-weather-backend.git
cd my-ski-weather-backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Run the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### View API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Response

```json
{
  "resort_name": "Sunshine Village",
  "location": "Banff, Canada",
  "coordinates": {
    "lat": 51.1164,
    "lon": -115.7631
  },
  "forecasts": [
    {
      "timestamp": "2025-11-23T18:00:00",
      "layers": [
        {
          "level": "Top",
          "altitude": 2730,
          "temperature": -8.0,
          "precipitation": 0.0,
          "condition": "Cloudy/Clear",
          "icon": "☁️"
        },
        ...
      ]
    }
  ]
}
```

## Snow Condition Algorithm

The API uses a sophisticated algorithm to determine snow conditions based on temperature and precipitation:

- **Champagne Powder** (❄️💎): Temp ≤ -12°C with precipitation
- **Powder** (❄️): -12°C < Temp ≤ -3°C with precipitation  
- **Snow** (🌨️): -3°C < Temp ≤ 0.5°C with precipitation
- **Wet Snow/Sleet** (💧❄️): 0.5°C < Temp ≤ 2°C with precipitation
- **Rain** (🌧️): Temp > 2°C with precipitation
- **Cloudy/Clear** (☁️): No precipitation

## Development Roadmap

- [ ] Integration with real weather API (Meteomatics)
- [ ] Add more ski resorts (Japan, Europe, USA)
- [ ] Implement caching layer
- [ ] Add 15-day extended forecast
- [ ] Calculate freezing level (0°C line) visualization data
- [ ] Add wind speed and direction data
- [ ] Deploy to cloud platform (AWS/Vercel)

## Technology Stack

- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **Python 3.8+**: Programming language

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Acknowledgments

Inspired by Snow-Forecast.com and built following recommendations from Gemini AI for creating a modern ski weather forecasting backend.
