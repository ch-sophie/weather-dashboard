import os
import json
import requests
from datetime import datetime

#CONFIG 
LANDING_ZONE = "./data/weather_landing/raw"
CITIES = {
    "New_York": {"lat": 40.7128, "lon": -74.0060},
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Tokyo": {"lat": 35.6895, "lon": 139.6917}
}

def fetch_weather_data(lat, lon):
    """Fetches raw weather metrics from Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m",
        "timezone": "auto"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status() # Raises an error for bad status codes (44, 500, etc.)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None

def save_to_landing_zone(data, city_name):
    """Saves the raw JSON data payload into the landing zone directory."""
    os.makedirs(LANDING_ZONE, exist_ok=True)
    
    # Generate an explicit timestamp for data audit tracking
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Add metadata tags directly inside the file before saving
    data["metadata"] = {
        "city": city_name,
        "extracted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    filename = f"{city_name.lower()}_{timestamp}.json"
    file_path = os.path.join(LANDING_ZONE, filename)
    
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
        
    print(f"Successfully landed raw data for {city_name} at: {file_path}")

def main():
    """Main execution block loop."""
    print("Starting weather data extraction pipeline...")
    
    for city, coords in CITIES.items():
        raw_weather = fetch_weather_data(coords["lat"], coords["lon"])
        
        if raw_weather:
            save_to_landing_zone(raw_weather, city)
            
    print("Extraction pipeline step finished successfully.")

if __name__ == "__main__":
    main()