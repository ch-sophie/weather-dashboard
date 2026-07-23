import os
print(os.environ.get("JAVA_HOME"))

from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("test").getOrCreate()
print(spark.version)

from pyspark.sql import SparkSession

# Initialize a basic test session
spark = SparkSession.builder \
    .appName("Test") \
    .master("local[*]") \
    .getOrCreate()

print("Success! Spark is completely working locally.")
spark.stop()

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, input_file_name

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Weather_Bronze") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# 1. Read all JSON files from landing zone
# Use multiLine=True because the Open-Meteo JSON files have nested structures
raw_df = spark.read \
    .option("multiLine", "true") \
    .json("./data/weather_landing/raw/*.json")

# 2. Add system metadata columns for auditing
bronze_df = raw_df \
    .withColumn("ingested_at", current_timestamp()) \
    .withColumn("source_file", input_file_name())

# 3. Write data to the Bronze Delta Table
# Delta format ensures ACID transactions and history tracking
bronze_df.write \
    .format("delta") \
    .mode("append") \
    .save("./data/delta/weather_bronze")

print("Bronze layer processed successfully.")