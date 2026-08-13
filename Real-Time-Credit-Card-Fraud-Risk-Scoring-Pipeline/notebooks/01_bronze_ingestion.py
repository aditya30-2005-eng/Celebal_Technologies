from __future__ import annotations

from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, StringType, StructField, StructType

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
    dbutils.widgets.text("raw_data_path", DEFAULT_CONFIG.input_path, "Raw transaction CSV directory")
    dbutils.widgets.text("bronze_checkpoint", DEFAULT_CONFIG.bronze_checkpoint, "Bronze checkpoint")
    raw_data_path = dbutils.widgets.get("raw_data_path")
    checkpoint_path = dbutils.widgets.get("bronze_checkpoint")
else:
    raw_data_path = DEFAULT_CONFIG.input_path
    checkpoint_path = DEFAULT_CONFIG.bronze_checkpoint

transaction_schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("card_id", StringType(), True),
    StructField("transaction_time", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("merchant", StringType(), True),
    StructField("merchant_category", StringType(), True),
    StructField("location", StringType(), True),
])

bronze_table = "fraud_db.bronze_transactions"


def table_exists(full_table_name: str) -> bool:
    db, tbl = full_table_name.split(".", 1) if "." in full_table_name else (spark.catalog.currentCatalog(), full_table_name)
    return any(t.name == tbl and t.database == db for t in spark.catalog.listTables(db))


spark.sql("CREATE DATABASE IF NOT EXISTS fraud_db")

if not table_exists(bronze_table):
    spark.createDataFrame([], transaction_schema).write.format("delta").saveAsTable(bronze_table)

raw_stream = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .option("header", "true")
    .option("inferSchema", "false")
    .schema(transaction_schema)
    .option("cloudFiles.includeExistingFiles", "true")
    .load(raw_data_path)
)

batch_hash = F.sha2(
    F.concat_ws(
        "|",
        F.coalesce(F.col("transaction_id"), F.lit("")),
        F.coalesce(F.col("customer_id"), F.lit("")),
        F.coalesce(F.col("card_id"), F.lit("")),
        F.coalesce(F.col("transaction_time"), F.lit("")),
        F.coalesce(F.col("amount"), F.lit("")),
        F.coalesce(F.col("merchant"), F.lit("")),
        F.coalesce(F.col("merchant_category"), F.lit("")),
        F.coalesce(F.col("location"), F.lit("")),
    ),
    256,
)

bronze_ready = (
    raw_stream
    .withColumn("ingest_timestamp", F.current_timestamp())
    .withColumn("source_file", F.input_file_name())
    .withColumn("raw_record_hash", batch_hash)
    .withColumn("batch_id", F.lit("stream-batch"))
)


def upsert_bronze(micro_batch_df, batch_id):
    if micro_batch_df.rdd.isEmpty():
        return
    deduped = micro_batch_df.dropDuplicates(["raw_record_hash"]).filter(F.col("transaction_id").isNotNull())
    if deduped.rdd.isEmpty():
        return
    delta_table = DeltaTable.forName(spark, bronze_table)
    delta_table.alias("t").merge(
        deduped.alias("s"),
        "t.raw_record_hash = s.raw_record_hash"
    ).whenNotMatchedInsertAll().execute()


query = (
    bronze_ready.writeStream
    .format("delta")
    .option("checkpointLocation", checkpoint_path)
    .foreachBatch(upsert_bronze)
    .outputMode("append")
    .trigger(availableNow=True)
    .start()
)
query.awaitTermination()
