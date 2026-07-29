import streamlit as st
import requests

st.set_page_config(page_title="Weather Search", page_icon="🌤️")


def geocode_city(city_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 5}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json().get("results", [])


def fetch_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m",
        "daily": "sunrise,sunset",
        "timezone": "auto",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


st.title("🌤️ City Weather Search")

query = st.text_input("Search for a city", placeholder="e.g. Osaka, Brussels, Nairobi")

if query:
    matches = geocode_city(query)

    if not matches:
        st.warning(f"No results found for '{query}'. Try a different spelling.")
    else:
        # If multiple matches (common city names), let user pick
        if len(matches) > 1:
            options = [
                f"{m['name']}, {m.get('admin1', '')} {m.get('country', '')}".strip()
                for m in matches
            ]
            selected = st.selectbox("Multiple matches found — select one:", options)
            city = matches[options.index(selected)]
        else:
            city = matches[0]

        weather = fetch_weather(city["latitude"], city["longitude"])
        current = weather.get("current", {})

        st.subheader(f"{city['name']}, {city.get('country', '')}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Temperature", f"{current.get('temperature_2m')} °C")
        col2.metric("Feels Like", f"{current.get('apparent_temperature')} °C")
        col3.metric("Humidity", f"{current.get('relative_humidity_2m')}%")

        col4, col5 = st.columns(2)
        col4.metric("Precipitation", f"{current.get('precipitation')} mm")
        col5.metric("Wind Speed", f"{current.get('wind_speed_10m')} km/h")

        daily = weather.get("daily", {})
        sunrise_list = daily.get("sunrise", [])
        sunset_list = daily.get("sunset", [])

        if sunrise_list and sunset_list:
            # Times come back as "YYYY-MM-DDTHH:MM"; show just the time portion
            sunrise_time = sunrise_list[0].split("T")[1]
            sunset_time = sunset_list[0].split("T")[1]

            col6, col7 = st.columns(2)
            col6.metric("🌅 Sunrise", sunrise_time)
            col7.metric("🌇 Sunset", sunset_time)

        st.caption(f"Last updated: {current.get('time')} · Timezone: {weather.get('timezone')}")