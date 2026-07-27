from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, input_file_name
from delta import configure_spark_with_delta_pip

def get_spark_session():
    builder = SparkSession.builder \
        .appName("Weather_Bronze") \
        .master("local[*]") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

    return configure_spark_with_delta_pip(builder).getOrCreate()

def run_bronze_layer(
    spark,
    input_path="./data/weather_landing/raw/*.json",
    output_path="./data/delta/weather_bronze",
):
    # 1. Read all JSON files from landing zone
    # Use multiLine=True because the Open-Meteo JSON files have nested structures
    raw_df = spark.read \
        .option("multiLine", "true") \
        .json(input_path)

    # 2. Add system metadata columns for auditing
    bronze_df = raw_df \
        .withColumn("ingested_at", current_timestamp()) \
        .withColumn("source_file", input_file_name())

    # 3. Write data to the Bronze Delta Table
    # Delta format ensures ACID transactions and history tracking
    bronze_df.write \
        .format("delta") \
        .mode("append") \
        .save(output_path)

    row_count = bronze_df.count()
    print(f"Bronze layer processed successfully. Rows written: {row_count}")

if __name__ == "__main__":
    spark = get_spark_session()
    try:
        run_bronze_layer(spark)
    finally:
        spark.stop()