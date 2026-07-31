import streamlit as st
import requests
from datetime import datetime

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
        "daily": "sunrise,sunset,temperature_2m_max,temperature_2m_min,weathercode",
        "timezone": "auto",
        "forecast_days": 6,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

WEATHER_CODES = {
    0: ("☀️", "Clear"),
    1: ("🌤️", "Mostly clear"),
    2: ("⛅", "Partly cloudy"),
    3: ("☁️", "Overcast"),
    45: ("🌫️", "Fog"),
    48: ("🌫️", "Fog"),
    51: ("🌦️", "Light drizzle"),
    53: ("🌦️", "Drizzle"),
    55: ("🌦️", "Heavy drizzle"),
    61: ("🌧️", "Light rain"),
    63: ("🌧️", "Rain"),
    65: ("🌧️", "Heavy rain"),
    71: ("🌨️", "Light snow"),
    73: ("🌨️", "Snow"),
    75: ("🌨️", "Heavy snow"),
    80: ("🌦️", "Rain showers"),
    81: ("🌦️", "Rain showers"),
    82: ("⛈️", "Violent showers"),
    95: ("⛈️", "Thunderstorm"),
    96: ("⛈️", "Thunderstorm w/ hail"),
    99: ("⛈️", "Thunderstorm w/ hail"),
}

def describe_weather_code(code):
    return WEATHER_CODES.get(code, ("🌡️", "Unknown"))

st.title("🌤️ City Weather Search")

col_input, col_button = st.columns([4, 1])
with col_input:
    query = st.text_input("Search for a city", placeholder="Brussels", label_visibility="collapsed")
with col_button:
    search_clicked = st.button("Search", use_container_width=True)

if search_clicked and query:
    st.session_state["matches"] = geocode_city(query)
    st.session_state["query"] = query

if "matches" in st.session_state:
    matches = st.session_state["matches"]
    query = st.session_state["query"]

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

        local_time_str = current.get("time")
        local_time_html = ""
        if local_time_str:
            local_dt = datetime.strptime(local_time_str, "%Y-%m-%dT%H:%M")
            local_time_html = f" <span style='color: #1134A6; font-size: 0.6em;'>{local_dt.strftime('%A, %b %d · %I:%M %p')}</span>"
 
        st.markdown(
            f"## {city['name']}, {city.get('country', '')}{local_time_html}",
            unsafe_allow_html=True,
        )

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

        st.divider()
        st.subheader("📅 5-Day Forecast")

        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        codes = daily.get("weathercode", [])

        # Skip index 0 (today, already shown above) and show the next 5 days
        forecast_cols = st.columns(5)
        for i, col in enumerate(forecast_cols, start=1):
            if i >= len(dates):
                break
            emoji, label = describe_weather_code(codes[i])
            with col:
                st.markdown(f"**{dates[i]}**")
                st.markdown(f"<span style='font-size: 2rem'>{emoji}</span>", unsafe_allow_html=True)
                st.caption(label)
                st.markdown(f"**{max_temps[i]:.0f}°** / {min_temps[i]:.0f}°")