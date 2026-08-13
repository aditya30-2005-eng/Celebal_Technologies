from __future__ import annotations

from delta.tables import DeltaTable
from pyspark.sql import DataFrame, functions as F
from pyspark.sql.types import DoubleType, StringType, StructField, StructType

from src.config import DEFAULT_CONFIG
from src.fraud_rules import standardize_category, standardize_location

if "dbutils" in globals():
    try:
        dbutils.widgets.remove("silver_checkpoint")
    except Exception:
        pass
    try:
        dbutils.widgets.remove("customer_profile_path")
    except Exception:
        pass
    dbutils.widgets.text("silver_checkpoint", DEFAULT_CONFIG.silver_checkpoint, "Silver checkpoint")
    dbutils.widgets.text("customer_profile_path", DEFAULT_CONFIG.customer_profile_path, "Customer profile path")
    silver_checkpoint = dbutils.widgets.get("silver_checkpoint")
    customer_profile_path = dbutils.widgets.get("customer_profile_path")
else:
    silver_checkpoint = DEFAULT_CONFIG.silver_checkpoint
    customer_profile_path = DEFAULT_CONFIG.customer_profile_path

customer_schema = StructType([
    StructField("customer_id", StringType(), True),
    StructField("home_location", StringType(), True),
    StructField("avg_spend_per_day", DoubleType(), True),
    StructField("preferred_category", StringType(), True),
])

silver_table = "fraud_db.silver_transactions"
rejected_table = "fraud_db.silver_rejected_transactions"


def table_exists(full_table_name: str) -> bool:
    db, tbl = full_table_name.split(".", 1) if "." in full_table_name else (spark.catalog.currentCatalog(), full_table_name)
    return any(t.name == tbl and t.database == db for t in spark.catalog.listTables(db))


customer_df = (
    spark.read.format("csv")
    .option("header", "true")
    .schema(customer_schema)
    .load(customer_profile_path)
)

standardize_category_udf = F.udf(lambda v: standardize_category(v), StringType())
standardize_location_udf = F.udf(lambda v: standardize_location(v), StringType())


def build_quality_flags(df: DataFrame) -> DataFrame:
    return (
        df
        .withColumn("transaction_timestamp", F.to_timestamp(F.col("transaction_time"), "yyyy-MM-dd HH:mm:ss"))
        .withColumn("amount", F.col("amount").cast("double"))
        .withColumn("merchant", F.trim(F.col("merchant")))
        .withColumn("merchant_category", standardize_category_udf(F.trim(F.col("merchant_category"))))
        .withColumn("location", standardize_location_udf(F.trim(F.col("location"))))
        .withColumn("customer_id", F.trim(F.col("customer_id")))
        .withColumn("card_id", F.trim(F.col("card_id")))
        .withColumn("transaction_id", F.trim(F.col("transaction_id")))
        .withColumn("invalid_reasons", F.array(
            F.when((F.col("transaction_id").isNull()) | (F.trim(F.col("transaction_id")) == ""), F.lit("transaction_id_missing")).otherwise(None),
            F.when((F.col("customer_id").isNull()) | (F.trim(F.col("customer_id")) == ""), F.lit("customer_id_missing")).otherwise(None),
            F.when((F.col("card_id").isNull()) | (F.trim(F.col("card_id")) == ""), F.lit("card_id_missing")).otherwise(None),
            F.when((F.col("amount").isNull()) | (F.col("amount") <= 0), F.lit("amount_invalid")).otherwise(None),
            F.when(F.col("transaction_timestamp").isNull(), F.lit("timestamp_missing")).otherwise(None),
            F.when((F.col("merchant_category").isNull()) | (F.trim(F.col("merchant_category")) == ""), F.lit("merchant_category_missing")).otherwise(None),
            F.when((F.col("location").isNull()) | (F.trim(F.col("location")) == ""), F.lit("location_missing")).otherwise(None),
            F.when(F.col("transaction_timestamp") > F.current_timestamp(), F.lit("future_timestamp")).otherwise(None),
        ))
        .withColumn("invalid_reasons", F.expr("filter(invalid_reasons, x -> x IS NOT NULL)"))
        .withColumn("is_valid", F.size(F.col("invalid_reasons")) == 0)
        .withColumn("data_quality_score", F.when(F.size(F.col("invalid_reasons")) == 0, F.lit(1.0)).otherwise(F.lit(0.0)))
    )


def ensure_target_tables():
    if not table_exists(silver_table):
        spark.createDataFrame([], spark.table("fraud_db.bronze_transactions").limit(0).schema).write.format("delta").option("delta.enableChangeDataFeed", "true").saveAsTable(silver_table)
    if not table_exists(rejected_table):
        spark.table(silver_table).limit(0).write.format("delta").saveAsTable(rejected_table)


ensure_target_tables()


def process_silver_batch(micro_batch_df, batch_id):
    if micro_batch_df.rdd.isEmpty():
        return

    df = (
        micro_batch_df
        .withColumnRenamed("transaction_time", "transaction_time_raw")
        .withColumn("transaction_time", F.col("transaction_time_raw"))
    )
    df = build_quality_flags(df)
    df = df.join(customer_df, on="customer_id", how="left")

    valid_df = (
        df.filter(F.col("is_valid"))
        .withColumn("transaction_date", F.to_date("transaction_timestamp"))
        .withColumn("transaction_hour", F.hour("transaction_timestamp"))
        .withColumn("is_weekend", F.dayofweek("transaction_timestamp").isin(1, 7))
        .withColumn("processed_at", F.current_timestamp())
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
            "processed_at",
        )
    )

    invalid_df = (
        df.filter(~F.col("is_valid"))
        .withColumn("rejection_reason", F.concat_ws("; ", "invalid_reasons"))
        .withColumn("rejected_at", F.current_timestamp())
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
            "source_file",
        )
    )

    if not valid_df.rdd.isEmpty():
        delta_target = DeltaTable.forName(spark, silver_table)
        delta_target.alias("t").merge(
            valid_df.alias("s"),
            "t.transaction_id = s.transaction_id"
        ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

    if not invalid_df.rdd.isEmpty():
        rejected_target = DeltaTable.forName(spark, rejected_table)
        rejected_target.alias("t").merge(
            invalid_df.alias("s"),
            "t.transaction_id = s.transaction_id"
        ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()


query = (
    spark.readStream.table("fraud_db.bronze_transactions")
    .writeStream
    .foreachBatch(process_silver_batch)
    .outputMode("append")
    .option("checkpointLocation", silver_checkpoint)
    .trigger(availableNow=True)
    .start()
)
query.awaitTermination()
