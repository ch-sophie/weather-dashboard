# Weather Data Pipeline
A data engineering pipeline that extracts live weather data for cities around the world, processes it through a medallion architecture (Bronze → Silver → Gold) using PySpark and Delta Lake, and visualizes the results in a Streamlit dashboard. Orchestrated with Apache Airflow running in Docker.

**Check the app here: [Weather app](https://weather-dashboard-7qy8.onrender.com)**

## Architecture
```
Open-Meteo API
      │
      ▼
┌─────────────────┐
│  extract_weather │  Fetches current weather for each city, lands raw JSON
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  Bronze Layer    │  Appends raw JSON into a Delta table, adds ingestion metadata
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  Silver Layer    │  Flattens nested fields, casts types, dedupes, drops nulls
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  Gold Layer      │  Latest reading per city + aggregated summary by continent
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  Streamlit App   │  Dashboard (Gold data) + live city search (on-demand API)
└─────────────────┘
```

## Project Structure
```
weather-pipeline/
├── src/
│   └── extract_weather.py         # Fetches weather data, writes raw JSON to landing zone
├── pipeline/
│   ├── bronze.py                  # Raw JSON → Bronze Delta table
│   ├── silver.py                  # Bronze → cleaned, flattened Silver Delta table
│   └── gold.py                    # Silver → Gold: latest snapshot + continent summary
├── data/
│   ├── weather_landing/raw/       # Raw JSON files land here
│   └── delta/                     # Bronze, Silver, Gold Delta tables
├── dashboard.py                   # Streamlit dashboard for Gold layer data
├── app.py                         # Streamlit live city search app
└── airflow/
    ├── docker-compose.yml         # Airflow + Postgres services
    ├── Dockerfile                 # Airflow image with Java 17 + PySpark + Delta
    ├── dags/
    │   └── weather_pipeline_dag.py
    ├── logs/
    └── plugins/
```

## Tech Stack
- **Python** — extraction and orchestration scripts
- **PySpark 4.1.1** — distributed data processing
- **Delta Lake** — ACID-compliant table storage for Bronze/Silver/Gold layers
- **Apache Airflow** — daily pipeline scheduling and orchestration
- **Docker / Docker Compose** — containerized Airflow environment
- **Streamlit** — interactive dashboard and live search app
- **Open-Meteo API** — free weather data and geocoding

## Setup
### Prerequisites
- Python 3.11+
- Java 17 (required by PySpark 4.x)
- Docker Desktop (for running Airflow)

### 1. Install Python dependencies
```bash
pip install pyspark delta-spark requests streamlit pandas
```

### 2. Set JAVA_HOME (local development)
```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 17)   #macOS
export PATH="$JAVA_HOME/bin:$PATH"
```

### 3. Run the pipeline manually
```bash
python3 src/extract_weather.py
python3 pipeline/bronze.py
python3 pipeline/silver.py
python3 pipeline/gold.py
```

### 4. View the dashboard
```bash
streamlit run dashboard.py
```

### 5. Run the live city search app
```bash
streamlit run app/app.py
```

## Running with Airflow
The pipeline can be automated to run daily using Airflow inside Docker.
```bash
cd airflow
mkdir -p logs plugins
docker-compose build
docker-compose up airflow-init
docker-compose up -d
```

Visit `http://localhost:8080` (default login: `admin` / `admin`), enable the `weather_medallion_pipeline` DAG, and trigger it manually or let it run on its daily schedule.

**Note:** Airflow only triggers scheduled runs while its containers are running. If Docker is stopped or your machine is off, the daily schedule won't fire until it's started again — this setup is intended for local development/demo purposes rather than unattended production scheduling.

To stop Airflow:
```bash
docker-compose down
```

## Data Model
### Bronze
Raw API responses as landed, with added `ingested_at` and `source_file` audit columns.

### Silver
Flattened and typed columns: `city`, `country`, `continent`, `latitude`, `longitude`, `elevation`, `weather_timestamp`, `temperature_celsius`, `relative_humidity_pct`, `apparent_temperature_celsius`, `precipitation_mm`, `wind_speed_kmh`. Deduplicated on `(city, weather_timestamp)`; rows missing essential fields are dropped.

### Gold
Two tables:
- **`weather_gold_latest`** — one row per city, most recent reading only
- **`weather_gold_summary`** — aggregated stats (avg/max/min temperature, avg humidity, avg wind speed) grouped by continent

## Adding More Cities
Add entries to the `CITIES` dictionary in `src/extract_weather.py`:
```python
CITIES = {
    "Bangkok": {"lat": 13.7563, "lon": 100.5018, "country": "Thailand", "continent": "Asia"},
}
```

Then rerun the pipeline in order (extract → bronze → silver → gold) to pick up the new cities.

#### Known Limitations
- Airflow's daily schedule only runs while Docker is actively running; it is not a substitute for a persistent server or cloud-hosted orchestration for true unattended automation.
- The live search app queries the Open-Meteo API directly and does not go through the Spark/Delta pipeline, by design, to keep search results fast.
- Silver and Gold layers fully rebuild (`overwrite`) on each run rather than incrementally processing only new data.
