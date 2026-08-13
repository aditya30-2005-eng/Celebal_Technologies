from __future__ import annotations

from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from src.config import DEFAULT_CONFIG

if "dbutils" in globals():
    try:
        dbutils.widgets.remove("gold_checkpoint")
    except Exception:
        pass
    dbutils.widgets.text("gold_checkpoint", DEFAULT_CONFIG.gold_checkpoint, "Gold checkpoint")
    gold_checkpoint = dbutils.widgets.get("gold_checkpoint")
else:
    gold_checkpoint = DEFAULT_CONFIG.gold_checkpoint

silver_table = "fraud_db.silver_transactions"
features_table = "fraud_db.gold_transaction_features"
alerts_table = "fraud_db.gold_high_risk_transactions"
state_table = "fraud_db.gold_customer_behavior_state"


def table_exists(full_table_name: str) -> bool:
    db, tbl = full_table_name.split(".", 1) if "." in full_table_name else (spark.catalog.currentCatalog(), full_table_name)
    return any(t.name == tbl and t.database == db for t in spark.catalog.listTables(db))


if not table_exists(features_table):
    spark.table(silver_table).limit(0).write.format("delta").option("delta.enableChangeDataFeed", "true").saveAsTable(features_table)

if not table_exists(alerts_table):
    spark.table(silver_table).limit(0).write.format("delta").option("delta.enableChangeDataFeed", "true").saveAsTable(alerts_table)

if not table_exists(state_table):
    spark.table(silver_table).limit(0).write.format("delta").option("delta.enableChangeDataFeed", "true").saveAsTable(state_table)


def process_gold_batch(micro_batch_df, batch_id):
    if micro_batch_df.rdd.isEmpty():
        return

    history_df = spark.table(silver_table)
    combined_df = history_df.unionByName(micro_batch_df)

    customer_order = Window.partitionBy("customer_id").orderBy(F.col("transaction_timestamp").cast("long"))
    customer_1h = Window.partitionBy("customer_id").orderBy(F.col("transaction_timestamp").cast("long")).rangeBetween(-3600, 0)
    customer_15m = Window.partitionBy("customer_id").orderBy(F.col("transaction_timestamp").cast("long")).rangeBetween(-900, 0)
    card_window = Window.partitionBy("customer_id", "card_id")
    merchant_window = Window.partitionBy("merchant")
    customer_avg_window = Window.partitionBy("customer_id")

    prev_location = F.lag("location").over(customer_order)
    prev_time = F.lag("transaction_timestamp").over(customer_order)

    enriched = (
        combined_df
        .withColumn("transaction_timestamp", F.to_timestamp(F.col("transaction_timestamp")))
        .withColumn("previous_location", prev_location)
        .withColumn("previous_transaction_time", prev_time)
        .withColumn("minutes_since_previous", F.when(
            F.col("previous_transaction_time").isNotNull(),
            (F.unix_timestamp(F.col("transaction_timestamp")) - F.unix_timestamp(F.col("previous_transaction_time"))) / 60.0
        ).otherwise(F.lit(None)))
        .withColumn("transaction_count_1h", F.count("*").over(customer_1h))
        .withColumn("transaction_amount_1h", F.sum("amount").over(customer_1h))
        .withColumn("average_transaction_amount", F.avg("amount").over(customer_avg_window))
        .withColumn("transactions_per_card", F.count("*").over(card_window))
        .withColumn("merchant_frequency", F.count("*").over(merchant_window))
        .withColumn("location_change_indicator", F.when(
            (F.col("previous_location").isNotNull())
            & (F.col("previous_location") != F.col("location"))
            & (F.col("minutes_since_previous") <= 30),
            F.lit(1)
        ).otherwise(F.lit(0)))
        .withColumn("time_since_previous_transaction", F.when(
            F.col("previous_transaction_time").isNotNull(),
            F.unix_timestamp(F.col("transaction_timestamp")) - F.unix_timestamp(F.col("previous_transaction_time"))
        ).otherwise(F.lit(0.0)))
        .withColumn("amount_deviation", F.when(
            F.col("average_transaction_amount").isNotNull() & (F.col("average_transaction_amount") > 0),
            F.abs(F.col("amount") - F.col("average_transaction_amount")) / F.col("average_transaction_amount")
        ).otherwise(F.lit(0.0)))
        .withColumn("unusual_hour_indicator", F.when(F.hour(F.col("transaction_timestamp")).between(0, 5), F.lit(1)).otherwise(F.lit(0)))
        .withColumn("high_amount_indicator", F.when(
            (F.col("amount") >= F.coalesce(F.col("avg_spend_per_day"), F.lit(0.0)) * 3) |
            (F.col("amount") > 10000),
            F.lit(1)
        ).otherwise(F.lit(0)))
        .withColumn("velocity_flag", F.when(
            (F.count("*").over(customer_15m) > 5) | (F.col("transaction_count_1h") > 3),
            F.lit(1)
        ).otherwise(F.lit(0)))
        .withColumn("high_amount_flag", F.when(F.col("high_amount_indicator") == 1, F.lit(1)).otherwise(F.lit(0)))
        .withColumn("location_hop_flag", F.when(F.col("location_change_indicator") == 1, F.lit(1)).otherwise(F.lit(0)))
        .withColumn("unusual_hour_flag", F.when(F.col("unusual_hour_indicator") == 1, F.lit(1)).otherwise(F.lit(0)))
        .withColumn("amount_deviation_flag", F.when(F.col("amount_deviation") > 1.5, F.lit(1)).otherwise(F.lit(0)))
        .withColumn("merchant_frequency_flag", F.when(F.col("merchant_frequency") > 15, F.lit(1)).otherwise(F.lit(0)))
    )

    score_expr = (
        F.when(F.col("high_amount_flag") == 1, 25).otherwise(0) +
        F.when(F.col("velocity_flag") == 1, 20).otherwise(0) +
        F.when(F.col("location_hop_flag") == 1, 20).otherwise(0) +
        F.when(F.col("unusual_hour_flag") == 1, 15).otherwise(0) +
        F.when(F.col("amount_deviation_flag") == 1, 20).otherwise(0) +
        F.when(F.col("merchant_frequency_flag") == 1, 10).otherwise(0)
    )

    scored = (
        enriched
        .withColumn("risk_score", F.greatest(F.lit(0.0), F.least(F.lit(100.0), score_expr.cast("double"))))
        .withColumn("risk_level", F.when(F.col("risk_score") <= 30, F.lit("LOW")).when(F.col("risk_score") <= 70, F.lit("MEDIUM")).otherwise(F.lit("HIGH")))
        .withColumn("fraud_rules_triggered", F.array(
            F.when(F.col("high_amount_flag") == 1, F.lit("high_amount_flag")).otherwise(None),
            F.when(F.col("velocity_flag") == 1, F.lit("velocity_flag")).otherwise(None),
            F.when(F.col("location_hop_flag") == 1, F.lit("location_hop_flag")).otherwise(None),
            F.when(F.col("unusual_hour_flag") == 1, F.lit("unusual_hour_flag")).otherwise(None),
            F.when(F.col("amount_deviation_flag") == 1, F.lit("amount_deviation_flag")).otherwise(None),
            F.when(F.col("merchant_frequency_flag") == 1, F.lit("merchant_frequency_flag")).otherwise(None),
        ))
        .withColumn("fraud_rules_triggered", F.expr("filter(fraud_rules_triggered, x -> x IS NOT NULL)"))
        .withColumn("fraud_prediction", F.col("risk_score") >= 71)
        .withColumn("processed_at", F.current_timestamp())
    )

    features = scored.filter(F.col("transaction_id").isNotNull()).select(
        "transaction_id",
        "customer_id",
        "card_id",
        "transaction_timestamp",
        "amount",
        "merchant",
        "merchant_category",
        "location",
        "transaction_count_1h",
        "transaction_amount_1h",
        "average_transaction_amount",
        "amount_deviation",
        "transactions_per_card",
        "merchant_frequency",
        "location_change_indicator",
        "time_since_previous_transaction",
        "unusual_hour_indicator",
        "high_amount_indicator",
        "velocity_flag",
        "high_amount_flag",
        "location_hop_flag",
        "unusual_hour_flag",
        "amount_deviation_flag",
        "merchant_frequency_flag",
        "risk_score",
        "risk_level",
        "fraud_prediction",
        "fraud_rules_triggered",
        "processed_at",
    )

    if not table_exists(features_table):
        features.limit(0).write.format("delta").option("delta.enableChangeDataFeed", "true").saveAsTable(features_table)
    DeltaTable.forName(spark, features_table).alias("t").merge(
        features.alias("s"),
        "t.transaction_id = s.transaction_id"
    ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

    high_risk = features.filter(F.col("fraud_prediction") == True).select(
        "transaction_id",
        "transaction_timestamp",
        "customer_id",
        "card_id",
        "amount",
        "merchant",
        "merchant_category",
        "location",
        "risk_score",
        "risk_level",
        "fraud_prediction",
        "high_amount_flag",
        "velocity_flag",
        "location_hop_flag",
        "unusual_hour_flag",
        "amount_deviation_flag",
        "processed_at",
    ).withColumnRenamed("merchant", "merchant_id")

    if not table_exists(alerts_table):
        high_risk.limit(0).write.format("delta").option("delta.enableChangeDataFeed", "true").saveAsTable(alerts_table)
    DeltaTable.forName(spark, alerts_table).alias("t").merge(
        high_risk.alias("s"),
        "t.transaction_id = s.transaction_id"
    ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

    customer_state = (
        spark.table(silver_table)
        .groupBy("customer_id", "card_id")
        .agg(
            F.max("transaction_timestamp").alias("last_transaction_time"),
            F.count("*").alias("transaction_count_30d"),
            F.avg("amount").alias("avg_amount_30d"),
            F.max("amount").alias("max_amount_30d"),
            F.sum("amount").alias("total_amount_30d"),
            F.max_by("location", "transaction_timestamp").alias("last_location"),
        )
        .withColumn("updated_at", F.current_timestamp())
    )

    if not table_exists(state_table):
        customer_state.limit(0).write.format("delta").option("delta.enableChangeDataFeed", "true").saveAsTable(state_table)
    DeltaTable.forName(spark, state_table).alias("t").merge(
        customer_state.alias("s"),
        "t.customer_id = s.customer_id AND t.card_id = s.card_id"
    ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()


query = (
    spark.readStream.table("fraud_db.silver_transactions")
    .writeStream
    .foreachBatch(process_gold_batch)
    .option("checkpointLocation", gold_checkpoint)
    .trigger(availableNow=True)
    .start()
)
query.awaitTermination()
