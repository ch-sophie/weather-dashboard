from pyspark.sql.functions import col, avg, max as spark_max, min as spark_min, count, row_number
from pyspark.sql.window import Window
from bronze import get_spark_session

def run_gold_layer(
    spark,
    input_path="./data/delta/weather_silver",
    latest_output_path="./data/delta/weather_gold_latest",
    summary_output_path="./data/delta/weather_gold_summary",
):
    silver_df = spark.read.format("delta").load(input_path)

    # 1. Latest reading per city (in case of multiple snapshots over time)
    window_spec = Window.partitionBy("city").orderBy(col("weather_timestamp").desc())

    latest_df = silver_df \
        .withColumn("row_num", row_number().over(window_spec)) \
        .filter(col("row_num") == 1) \
        .drop("row_num")

    latest_df.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .save(latest_output_path)

    latest_count = latest_df.count()
    print(f"Gold latest-snapshot table written. Rows: {latest_count}")

    # 2. Aggregate summary by continent
    summary_df = latest_df.groupBy("continent").agg(
        count("city").alias("city_count"),
        avg("temperature_celsius").alias("avg_temperature_celsius"),
        spark_max("temperature_celsius").alias("max_temperature_celsius"),
        spark_min("temperature_celsius").alias("min_temperature_celsius"),
        avg("humidity_pct" if "humidity_pct" in latest_df.columns else "relative_humidity_pct").alias("avg_humidity_pct"),
        avg("wind_speed_kmh").alias("avg_wind_speed_km/h"),
    )

    summary_df.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .save(summary_output_path)

    summary_count = summary_df.count()
    print(f"Gold continent-summary table written. Rows: {summary_count}")

if __name__ == "__main__":
    spark = get_spark_session()
    try:
        run_gold_layer(spark)
    finally:
        spark.stop()