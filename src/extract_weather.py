import os
import json
import time
import requests
from datetime import datetime

#CONFIG
LANDING_ZONE = "./data/weather_landing/raw"

CITIES = {
    "New_York": {"lat": 40.7128, "lon": -74.0060, "country": "USA", "continent": "North America"},
    "London": {"lat": 51.5074, "lon": -0.1278, "country": "UK", "continent": "Europe"},
    "Tokyo": {"lat": 35.6895, "lon": 139.6917, "country": "Japan", "continent": "Asia"},
    "Paris": {"lat": 48.8566, "lon": 2.3522, "country": "France", "continent": "Europe"},
    "Brussels": {"lat": 50.8503, "lon": 4.3517, "country": "Belgium", "continent": "Europe"},
    "Berlin": {"lat": 52.5200, "lon": 13.4050, "country": "Germany", "continent": "Europe"},
    "Madrid": {"lat": 40.4168, "lon": -3.7038, "country": "Spain", "continent": "Europe"},
    "Rome": {"lat": 41.9028, "lon": 12.4964, "country": "Italy", "continent": "Europe"},
    "Moscow": {"lat": 55.7558, "lon": 37.6173, "country": "Russia", "continent": "Europe"},
    "Dubai": {"lat": 25.2048, "lon": 55.2708, "country": "UAE", "continent": "Asia"},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "country": "India", "continent": "Asia"},
    "Beijing": {"lat": 39.9042, "lon": 116.4074, "country": "China", "continent": "Asia"},
    "Shanghai": {"lat": 31.2304, "lon": 121.4737, "country": "China", "continent": "Asia"},
    "Singapore": {"lat": 1.3521, "lon": 103.8198, "country": "Singapore", "continent": "Asia"},
    "Sydney": {"lat": -33.8688, "lon": 151.2093, "country": "Australia", "continent": "Oceania"},
    "Sao_Paulo": {"lat": -23.5505, "lon": -46.6333, "country": "Brazil", "continent": "South America"},
    "Mexico_City": {"lat": 19.4326, "lon": -99.1332, "country": "Mexico", "continent": "North America"},
    "Cairo": {"lat": 30.0444, "lon": 31.2357, "country": "Egypt", "continent": "Africa"},
    "Lagos": {"lat": 6.5244, "lon": 3.3792, "country": "Nigeria", "continent": "Africa"},
    "Nairobi": {"lat": -1.2921, "lon": 36.8219, "country": "Kenya", "continent": "Africa"},
    "Toronto": {"lat": 43.6532, "lon": -79.3832, "country": "Canada", "continent": "North America"},
    "Montreal": {"lat": 45.5019, "lon": -73.5674, "country": "Canada", "continent": "North America"},
    "Los_Angeles": {"lat": 34.0522, "lon": -118.2437, "country": "USA", "continent": "North America"},
    "Reykjavik": {"lat": 64.1466, "lon": -21.9426, "country": "Iceland", "continent": "Europe"},
    "Zurich": {"lat": 47.3769, "lon": 8.5417, "country": "Switzerland", "continent": "Europe"},
}

def fetch_weather_data(lat, lon):
    """Fetches raw weather metrics from Open-Meteo API"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m",
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None

def save_to_landing_zone(data, city_name, coords):
    """Saves the raw JSON data payload into the landing zone directory"""
    os.makedirs(LANDING_ZONE, exist_ok=True)

    # Generate an explicit timestamp for data tracking
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Add metadata tags directly inside the file before saving
    data["metadata"] = {
        "city": city_name,
        "country": coords.get("country"),
        "continent": coords.get("continent"),
        "extracted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    filename = f"{city_name.lower()}_{timestamp}.json"
    file_path = os.path.join(LANDING_ZONE, filename)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Successfully landed raw data for {city_name} at: {file_path}")

def main():
    """Main execution block loop"""
    print(f"Starting weather data extraction pipeline for {len(CITIES)} cities...")

    success_count = 0
    failure_count = 0

    for city, coords in CITIES.items():
        raw_weather = fetch_weather_data(coords["lat"], coords["lon"])

        if raw_weather:
            save_to_landing_zone(raw_weather, city, coords)
            success_count += 1
        else:
            failure_count += 1

        time.sleep(0.2)

    print(f"Extraction pipeline finished. Success: {success_count}, Failed: {failure_count}")

if __name__ == "__main__":
    main()