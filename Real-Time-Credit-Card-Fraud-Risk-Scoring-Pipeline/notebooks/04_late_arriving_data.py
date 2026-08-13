from __future__ import annotations

from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
)

INPUT_TABLE = "fraud_db.bronze_transactions"
LATE_TABLE = "fraud_db.silver_late_arrivals"

LATE_CHECKPOINT = "/Volumes/workspace/fraud_db/credit_fraud_data/checkpoints/late"

WATERMARK_MINUTES = 120


def table_exists(full_table_name: str) -> bool:
    parts = full_table_name.split(".")

    if len(parts) == 2:
        database, table = parts
    else:
        database = spark.catalog.currentDatabase()
        table = full_table_name

    return any(
        t.name == table
        for t in spark.catalog.listTables(database)
    )


spark.sql("CREATE DATABASE IF NOT EXISTS fraud_db")


late_schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("card_id", StringType(), True),
    StructField("transaction_timestamp", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("merchant", StringType(), True),
    StructField("merchant_category", StringType(), True),
    StructField("location", StringType(), True),
    StructField("ingest_timestamp", StringType(), True),
    StructField("source_file", StringType(), True),
    StructField("reason", StringType(), True),
])


if not table_exists(LATE_TABLE):
    (
        spark.createDataFrame([], late_schema)
        .write
        .format("delta")
        .saveAsTable(LATE_TABLE)
    )


bronze_df = (
    spark.read
    .table(INPUT_TABLE)
    .withColumn(
        "transaction_timestamp",
        F.to_timestamp(
            F.col("transaction_time"),
            "yyyy-MM-dd HH:mm:ss"
        )
    )
)


if bronze_df.limit(1).count() == 0:
    print("No bronze records found.")
else:

    stats = (
        bronze_df
        .select(
            F.min("transaction_timestamp").alias("min_event_time"),
            F.max("transaction_timestamp").alias("max_event_time")
        )
        .collect()[0]
    )

    min_event_time = stats["min_event_time"]
    max_event_time = stats["max_event_time"]

    print("========================================")
    print("LATE ARRIVING DATA PIPELINE")
    print("========================================")
    print(f"Minimum event time : {min_event_time}")
    print(f"Maximum event time : {max_event_time}")
    print(f"Watermark          : {WATERMARK_MINUTES} minutes")

    if max_event_time is None:

        print("No valid transaction timestamps found.")

    else:

        watermark_time = (
            max_event_time
            - __import__("datetime").timedelta(
                minutes=WATERMARK_MINUTES
            )
        )

        print(f"Late threshold     : {watermark_time}")

        late_df = (
            bronze_df
            .filter(
                F.col("transaction_timestamp") < F.lit(watermark_time)
            )
            .withColumn(
                "ingest_timestamp",
                F.current_timestamp()
            )
            .withColumn(
                "reason",
                F.lit("beyond_watermark_120_minutes")
            )
            .select(
                "transaction_id",
                "customer_id",
                "card_id",
                "transaction_timestamp",
                "amount",
                "merchant",
                "merchant_category",
                "location",
                "ingest_timestamp",
                "source_file",
                "reason",
            )
        )

        late_count = late_df.count()

        print(f"Late records       : {late_count}")

        if late_count > 0:

            delta_table = DeltaTable.forName(
                spark,
                LATE_TABLE
            )

            (
                delta_table
                .alias("t")
                .merge(
                    late_df.alias("s"),
                    "t.transaction_id = s.transaction_id"
                )
                .whenMatchedUpdateAll()
                .whenNotMatchedInsertAll()
                .execute()
            )

            print("Late records successfully written.")

        else:

            print("No late-arriving records found.")

        print("========================================")
        print("LATE ARRIVING DATA PIPELINE COMPLETED")
        print("========================================")


display(
    spark.sql(
        f"""
        SELECT
            COUNT(*) AS late_records
        FROM {LATE_TABLE}
        """
    )
)