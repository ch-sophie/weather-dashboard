from pyspark.sql.functions import col, to_date, avg, max, min

# 1. Read from the Silver Delta Table
silver_data = spark.read.format("delta").load("./data/delta/weather_silver")

# 2. Calculate daily analytics per city
gold_df = silver_data.groupBy("city", to_date("weather_timestamp").alias("weather_date")) \
    .agg(
        avg("temperature_celsius").alias("avg_temp_c"),
        max("temperature_celsius").alias("max_temp_c"),
        min("temperature_celsius").alias("min_temp_c"),
        avg("relative_humidity_pct").alias("avg_humidity_pct"),
        max("wind_speed_kmh").alias("max_wind_speed_kmh")
    ) \
    .orderBy("weather_date", "city")

# 3. Write to Gold Delta Table
gold_df.write \
    .format("delta") \
    .mode("overwrite") \
    .save("./data/delta/weather_gold_daily_summary")

print("Gold layer metrics aggregated successfully.")