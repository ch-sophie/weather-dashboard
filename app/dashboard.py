import streamlit as st
import pandas as pd
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

st.set_page_config(page_title="Weather Dashboard", page_icon="🌍", layout="wide")

@st.cache_resource
def get_spark_session():
    builder = SparkSession.builder \
        .appName("Weather_Dashboard") \
        .master("local[*]") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    return configure_spark_with_delta_pip(builder).getOrCreate()

@st.cache_data
def load_gold_tables():
    spark = get_spark_session()
    latest_df = spark.read.format("delta").load("./data/delta/weather_gold_latest").toPandas()
    summary_df = spark.read.format("delta").load("./data/delta/weather_gold_summary").toPandas()
    return latest_df, summary_df

st.title("🌍 Weather Dashboard")

latest_df, summary_df = load_gold_tables()

# --- Top-level metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Cities Tracked", len(latest_df))
col2.metric("Global Avg Temp", f"{latest_df['temperature_celsius'].mean():.1f} °C")
col3.metric("Continents", len(summary_df))

st.divider()

# --- Continent summary ---
st.subheader("🌐 Summary by Continent")

summary_display = summary_df.sort_values("avg_temperature_celsius", ascending=False)
st.dataframe(
    summary_display.style.format({
        "avg_temperature_celsius": "{:.1f}",
        "max_temperature_celsius": "{:.1f}",
        "min_temperature_celsius": "{:.1f}",
        "avg_humidity_pct": "{:.0f}",
        "avg_wind_speed_kmh": "{:.1f}",
    }),
    use_container_width=True,
)

bar_col1, bar_col2 = st.columns(2)
with bar_col1:
    st.caption("Average Temperature by Continent")
    st.bar_chart(summary_df.set_index("continent")["avg_temperature_celsius"])
with bar_col2:
    st.caption("Average Wind Speed by Continent")
    st.bar_chart(summary_df.set_index("continent")["avg_wind_speed_kmh"])

st.divider()

# --- City-level table with filtering ---
st.subheader("🗺️ All Cities — Latest")

continents = ["All"] + sorted(latest_df["continent"].dropna().unique().tolist())
selected_continent = st.selectbox("Filter by continent", continents)

filtered_df = latest_df if selected_continent == "All" else latest_df[latest_df["continent"] == selected_continent]

display_cols = [
    "city", "country", "continent", "temperature_celsius",
    "apparent_temperature_celsius", "relative_humidity_pct",
    "precipitation_mm", "wind_speed_kmh", "weather_timestamp",
]
st.dataframe(
    filtered_df[display_cols].sort_values("temperature_celsius", ascending=False),
    use_container_width=True,
)

st.divider()

# --- Map ---
st.subheader("📍 Locations")
map_df = latest_df.rename(columns={"latitude": "lat", "longitude": "lon"})[["lat", "lon"]]
map_df = map_df.astype("float64")
st.map(map_df)