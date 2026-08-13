from __future__ import annotations

import sys

from delta.tables import DeltaTable
from pyspark.sql import DataFrame, functions as F
from pyspark.sql.types import DoubleType, StringType, StructField, StructType


project_root = "/Workspace/Users/1000019979@dit.edu.in/Celebal_Technologies/Real-Time-Credit-Card-Fraud-Risk-Scoring-Pipeline"

if project_root not in sys.path:
    sys.path.insert(0, project_root)


from src.config import DEFAULT_CONFIG
from src.fraud_rules import standardize_category, standardize_location


silver_checkpoint = DEFAULT_CONFIG.silver_checkpoint
customer_profile_path = DEFAULT_CONFIG.customer_profile_path

customer_schema = StructType([
    StructField("customer_id", StringType(), True),
    StructField("home_location", StringType(), True),
    StructField("avg_spend_per_day", DoubleType(), True),
    StructField("preferred_category", StringType(), True),
])

silver_table = DEFAULT_CONFIG.silver_table
rejected_table = DEFAULT_CONFIG.silver_rejected_table


customer_df = (
    spark.read
    .format("csv")
    .option("header", "true")
    .schema(customer_schema)
    .load(customer_profile_path)
)


standardize_category_udf = F.udf(
    standardize_category,
    StringType()
)

standardize_location_udf = F.udf(
    standardize_location,
    StringType()
)


def build_quality_flags(df: DataFrame) -> DataFrame:

    return (
        df
        .withColumn(
            "transaction_timestamp",
            F.to_timestamp(
                F.col("transaction_time"),
                "yyyy-MM-dd HH:mm:ss"
            )
        )
        .withColumn(
            "amount",
            F.col("amount").cast("double")
        )
        .withColumn(
            "merchant",
            F.trim(F.col("merchant"))
        )
        .withColumn(
            "merchant_category",
            standardize_category_udf(
                F.trim(F.col("merchant_category"))
            )
        )
        .withColumn(
            "location",
            standardize_location_udf(
                F.trim(F.col("location"))
            )
        )
        .withColumn(
            "customer_id",
            F.trim(F.col("customer_id"))
        )
        .withColumn(
            "card_id",
            F.trim(F.col("card_id"))
        )
        .withColumn(
            "transaction_id",
            F.trim(F.col("transaction_id"))
        )
        .withColumn(
            "invalid_reasons",
            F.array(
                F.when(
                    (F.col("transaction_id").isNull()) |
                    (F.trim(F.col("transaction_id")) == ""),
                    F.lit("transaction_id_missing")
                ),

                F.when(
                    (F.col("customer_id").isNull()) |
                    (F.trim(F.col("customer_id")) == ""),
                    F.lit("customer_id_missing")
                ),

                F.when(
                    (F.col("card_id").isNull()) |
                    (F.trim(F.col("card_id")) == ""),
                    F.lit("card_id_missing")
                ),

                F.when(
                    (F.col("amount").isNull()) |
                    (F.col("amount") <= 0),
                    F.lit("amount_invalid")
                ),

                F.when(
                    F.col("transaction_timestamp").isNull(),
                    F.lit("timestamp_missing")
                ),

                F.when(
                    (F.col("merchant_category").isNull()) |
                    (F.trim(F.col("merchant_category")) == ""),
                    F.lit("merchant_category_missing")
                ),

                F.when(
                    (F.col("location").isNull()) |
                    (F.trim(F.col("location")) == ""),
                    F.lit("location_missing")
                ),

                F.when(
                    F.col("transaction_timestamp") > F.current_timestamp(),
                    F.lit("future_timestamp")
                )
            )
        )
        .withColumn(
            "invalid_reasons",
            F.expr(
                "filter(invalid_reasons, x -> x IS NOT NULL)"
            )
        )
        .withColumn(
            "is_valid",
            F.size(F.col("invalid_reasons")) == 0
        )
        .withColumn(
            "data_quality_score",
            F.when(
                F.col("is_valid"),
                F.lit(1.0)
            ).otherwise(
                F.lit(0.0)
            )
        )
    )


def process_silver_batch(micro_batch_df, batch_id):

    if micro_batch_df.limit(1).count() == 0:
        return

    df = build_quality_flags(micro_batch_df)

    df = df.join(
        customer_df,
        on="customer_id",
        how="left"
    )

    valid_df = (
        df
        .filter(F.col("is_valid"))
        .withColumn(
            "transaction_date",
            F.to_date("transaction_timestamp")
        )
        .withColumn(
            "transaction_hour",
            F.hour("transaction_timestamp")
        )
        .withColumn(
            "is_weekend",
            F.dayofweek("transaction_timestamp").isin(1, 7)
        )
        .withColumn(
            "processed_at",
            F.current_timestamp()
        )
        .select(
            "transaction_id",
            "customer_id",
            "card_id",
            "transaction_timestamp",
            "transaction_date",
            "transaction_hour",
            "is_weekend",
            "amount",
            "merchant",
            "merchant_category",
            "location",
            "home_location",
            "avg_spend_per_day",
            "preferred_category",
            "is_valid",
            "invalid_reasons",
            "data_quality_score",
            "ingest_timestamp",
            "source_file",
            "processed_at"
        )
        .dropDuplicates(["transaction_id"])
    )

    invalid_df = (
        df
        .filter(~F.col("is_valid"))
        .withColumn(
            "rejection_reason",
            F.concat_ws(
                "; ",
                "invalid_reasons"
            )
        )
        .withColumn(
            "rejected_at",
            F.current_timestamp()
        )
        .select(
            "transaction_id",
            "customer_id",
            "card_id",
            "transaction_time",
            "amount",
            "merchant",
            "merchant_category",
            "location",
            "rejection_reason",
            "rejected_at",
            "source_file"
        )
        .dropDuplicates(["transaction_id"])
    )

    if valid_df.limit(1).count() > 0:

        if not spark.catalog.tableExists(silver_table):

            (
                valid_df
                .write
                .format("delta")
                .option(
                    "delta.enableChangeDataFeed",
                    "true"
                )
                .mode("overwrite")
                .saveAsTable(silver_table)
            )

        else:

            delta_target = DeltaTable.forName(
                spark,
                silver_table
            )

            (
                delta_target.alias("t")
                .merge(
                    valid_df.alias("s"),
                    "t.transaction_id = s.transaction_id"
                )
                .whenMatchedUpdateAll()
                .whenNotMatchedInsertAll()
                .execute()
            )

    if invalid_df.limit(1).count() > 0:

        if not spark.catalog.tableExists(rejected_table):

            (
                invalid_df
                .write
                .format("delta")
                .mode("overwrite")
                .saveAsTable(rejected_table)
            )

        else:

            rejected_target = DeltaTable.forName(
                spark,
                rejected_table
            )

            (
                rejected_target.alias("t")
                .merge(
                    invalid_df.alias("s"),
                    "t.transaction_id = s.transaction_id"
                )
                .whenMatchedUpdateAll()
                .whenNotMatchedInsertAll()
                .execute()
            )


query = (
    spark
    .readStream
    .table("fraud_db.bronze_transactions")
    .writeStream
    .foreachBatch(process_silver_batch)
    .outputMode("update")
    .option(
        "checkpointLocation",
        silver_checkpoint
    )
    .trigger(
        availableNow=True
    )
    .start()
)

query.awaitTermination()

print("========================================")
print("SILVER PIPELINE COMPLETED")
print("========================================")