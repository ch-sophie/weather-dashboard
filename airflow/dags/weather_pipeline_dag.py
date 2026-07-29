from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/airflow/weather_project"

default_args = {
    "owner": "admin",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="weather_medallion_pipeline",
    description="Daily extraction and medallion (bronze/silver/gold) processing of city weather data",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["weather", "medallion", "spark", "delta"],
) as dag:
    extract = BashOperator(
        task_id="extract_weather",
        bash_command=f"cd {PROJECT_DIR} && python3 src/extract_weather.py",
    )
    bronze = BashOperator(
        task_id="bronze_layer",
        bash_command=f"cd {PROJECT_DIR} && python3 pipeline/bronze.py",
    )
    silver = BashOperator(
        task_id="silver_layer",
        bash_command=f"cd {PROJECT_DIR} && python3 pipeline/silver.py",
    )
    gold = BashOperator(
        task_id="gold_layer",
        bash_command=f"cd {PROJECT_DIR} && python3 pipeline/gold.py",
    )

    extract >> bronze >> silver >> gold