from __future__ import annotations

from delta.tables import DeltaTable
from pyspark.sql import functions as F

from src.config import DEFAULT_CONFIG

if "dbutils" in globals():
    try:
        dbutils.widgets.remove("late_checkpoint")
    except Exception:
        pass
    dbutils.widgets.text("late_checkpoint", DEFAULT_CONFIG.late_checkpoint, "Late-arrivals checkpoint")
    late_checkpoint = dbutils.widgets.get("late_checkpoint")
else:
    late_checkpoint = DEFAULT_CONFIG.late_checkpoint

late_table = "fraud_db.silver_late_arrivals"


def table_exists(full_table_name: str) -> bool:
    db, tbl = full_table_name.split(".", 1) if "." in full_table_name else (spark.catalog.currentCatalog(), full_table_name)
    return any(t.name == tbl and t.database == db for t in spark.catalog.listTables(db))


watermarked_stream = (
    spark.readStream.table("fraud_db.bronze_transactions")
    .withColumn("transaction_timestamp", F.to_timestamp(F.col("transaction_time"), "yyyy-MM-dd HH:mm:ss"))
    .withWatermark("transaction_timestamp", "2 hours")
)


def route_late(micro_batch_df, batch_id):
    if micro_batch_df.rdd.isEmpty():
        return

    late_df = (
        micro_batch_df
        .withColumn("transaction_timestamp", F.to_timestamp(F.col("transaction_time"), "yyyy-MM-dd HH:mm:ss"))
        .filter(F.expr("transaction_timestamp < current_timestamp() - INTERVAL 2 HOURS"))
    )

    if late_df.rdd.isEmpty():
        return

    late_df = (
        late_df
        .withColumn("ingest_timestamp", F.current_timestamp())
        .withColumn("reason", F.lit("beyond_watermark_2_hours"))
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

    if not table_exists(late_table):
        late_df.limit(0).write.format("delta").saveAsTable(late_table)

    delta_table = DeltaTable.forName(spark, late_table)
    delta_table.alias("t").merge(
        late_df.alias("s"),
        "t.transaction_id = s.transaction_id"
    ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()


query = (
    watermarked_stream.writeStream
    .foreachBatch(route_late)
    .option("checkpointLocation", late_checkpoint)
    .trigger(availableNow=True)
    .start()
)
query.awaitTermination()
