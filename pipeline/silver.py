from pyspark.sql.functions import col, to_timestamp

# 1. Read from Bronze Delta Table
bronze_data = spark.read.format("delta").load("./data/delta/weather_bronze")

# 2. Flatten the nested "current" block and pull out metadata
silver_df = bronze_data.select(
    col("metadata.city").alias("city"),
    col("latitude").cast("float"),
    col("longitude").cast("float"),
    col("elevation").cast("float"),
    # Unpack the current weather nested object and fix types
    to_timestamp(col("current.time"), "yyyy-MM-dd'T'HH:mm").alias("weather_timestamp"),
    col("current.temperature_2m").cast("float").alias("temperature_celsius"),
    col("current.relative_humidity_2m").cast("int").alias("relative_humidity_pct"),
    col("current.apparent_temperature").cast("float").alias("apparent_temperature_celsius"),
    col("current.precipitation").cast("float").alias("precipitation_mm"),
    col("current.wind_speed_10m").cast("float").alias("wind_speed_kmh"),
    col("ingested_at")
)

# 3. Write to Silver Delta Table, partitioned by city for query optimization
silver_df.write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("city") \
    .save("./data/delta/weather_silver")

print("Silver layer cleaned and flattened successfully.")