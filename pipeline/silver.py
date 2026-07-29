from pyspark.sql.functions import col, to_timestamp
from bronze import get_spark_session

spark = get_spark_session()
#Read from Bronze Delta Table
bronze_data = spark.read.format("delta").load("./data/delta/weather_bronze")

#Flatten the nested "current" block and pull out metadata
silver_df = bronze_data.select(
    col("metadata.city").alias("city"),
    col("metadata.country").alias("country"),
    col("metadata.continent").alias("continent"),
    col("latitude").cast("float"),
    col("longitude").cast("float"),
    col("elevation").cast("float"),
    to_timestamp(col("current.time"), "yyyy-MM-dd'T'HH:mm").alias("weather_timestamp"),
    col("current.temperature_2m").cast("float").alias("temperature_celsius"),
    col("current.relative_humidity_2m").cast("int").alias("relative_humidity_pct"),
    col("current.apparent_temperature").cast("float").alias("apparent_temperature_celsius"),
    col("current.precipitation").cast("float").alias("precipitation_mm"),
    col("current.wind_speed_10m").cast("float").alias("wind_speed_kmh"),
    to_timestamp(col("metadata.extracted_at")).alias("extracted_at"),
    col("ingested_at"),
    col("source_file"),
)

#Data quality: drop rows missing essential fields
silver_df = silver_df.dropna(subset=["city", "weather_timestamp", "temperature_celsius"])

#Deduplicate: same city + same weather timestamp = same observation
silver_df = silver_df.dropDuplicates(["city", "weather_timestamp"])

#Write to Silver Delta Table, partitioned by city for query optimization
silver_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .partitionBy("city") \
    .save("./data/delta/weather_silver")

row_count = silver_df.count()
print(f"Silver layer cleaned and flattened successfully. Rows written: {row_count}")