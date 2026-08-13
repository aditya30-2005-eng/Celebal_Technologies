from __future__ import annotations

import sys

from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
)

project_root = "/Workspace/Users/1000019979@dit.edu.in/Celebal_Technologies/Real-Time-Credit-Card-Fraud-Risk-Scoring-Pipeline"

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config import DEFAULT_CONFIG


if "dbutils" in globals():
    try:
        dbutils.widgets.remove("raw_data_path")
    except Exception:
        pass

    try:
        dbutils.widgets.remove("bronze_checkpoint")
    except Exception:
        pass

    dbutils.widgets.text(
        "raw_data_path",
        DEFAULT_CONFIG.input_path,
        "Raw transaction CSV directory",
    )

    dbutils.widgets.text(
        "bronze_checkpoint",
        DEFAULT_CONFIG.bronze_checkpoint,
        "Bronze checkpoint",
    )

    raw_data_path = dbutils.widgets.get("raw_data_path")
    checkpoint_path = dbutils.widgets.get("bronze_checkpoint")
else:
    raw_data_path = DEFAULT_CONFIG.input_path
    checkpoint_path = DEFAULT_CONFIG.bronze_checkpoint


transaction_schema = StructType(
    [
        StructField("transaction_id", StringType(), True),
        StructField("customer_id", StringType(), True),
        StructField("card_id", StringType(), True),
        StructField("transaction_time", StringType(), True),
        StructField("amount", DoubleType(), True),
        StructField("merchant", StringType(), True),
        StructField("merchant_category", StringType(), True),
        StructField("location", StringType(), True),
    ]
)


bronze_table = DEFAULT_CONFIG.bronze_table


spark.sql("CREATE SCHEMA IF NOT EXISTS fraud_db")


raw_stream = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .option("header", "true")
    .option("inferSchema", "false")
    .option("cloudFiles.includeExistingFiles", "true")
    .option("pathGlobFilter", "transaction.csv")
    .schema(transaction_schema)
    .load(raw_data_path)
)


bronze_ready = (
    raw_stream
    .withColumn("ingest_timestamp", F.current_timestamp())
    .withColumn("source_file", F.col("_metadata.file_path"))
    .withColumn(
        "raw_record_hash",
        F.sha2(
            F.concat_ws(
                "|",
                F.coalesce(F.col("transaction_id"), F.lit("")),
                F.coalesce(F.col("customer_id"), F.lit("")),
                F.coalesce(F.col("card_id"), F.lit("")),
                F.coalesce(F.col("transaction_time"), F.lit("")),
                F.coalesce(F.col("amount").cast("string"), F.lit("")),
                F.coalesce(F.col("merchant"), F.lit("")),
                F.coalesce(F.col("merchant_category"), F.lit("")),
                F.coalesce(F.col("location"), F.lit("")),
            ),
            256,
        ),
    )
    .filter(F.col("transaction_id").isNotNull())
    .dropDuplicates(["raw_record_hash"])
)


query = (
    bronze_ready
    .writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", checkpoint_path)
    .option("mergeSchema", "true")
    .trigger(availableNow=True)
    .toTable(bronze_table)
)

query.awaitTermination()