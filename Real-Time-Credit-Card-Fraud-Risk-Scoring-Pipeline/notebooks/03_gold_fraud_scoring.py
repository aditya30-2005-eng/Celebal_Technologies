from __future__ import annotations

import sys

from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql.window import Window


project_root = "/Workspace/Users/1000019979@dit.edu.in/Celebal_Technologies/Real-Time-Credit-Card-Fraud-Risk-Scoring-Pipeline"

if project_root not in sys.path:
    sys.path.insert(0, project_root)


from src.config import DEFAULT_CONFIG


gold_checkpoint = DEFAULT_CONFIG.gold_checkpoint

silver_table = DEFAULT_CONFIG.silver_table
features_table = DEFAULT_CONFIG.gold_features_table
alerts_table = DEFAULT_CONFIG.gold_alerts_table
state_table = DEFAULT_CONFIG.customer_state_table


def table_exists(table_name: str) -> bool:
    return spark.catalog.tableExists(table_name)


def process_gold_batch(micro_batch_df, batch_id):

    if micro_batch_df.limit(1).count() == 0:
        return

    history_df = spark.table(silver_table)

    combined_df = (
        history_df
        .unionByName(micro_batch_df)
        .dropDuplicates(["transaction_id"])
    )

    customer_order = (
        Window
        .partitionBy("customer_id")
        .orderBy(
            F.col("transaction_timestamp").cast("long")
        )
    )

    customer_1h = (
        Window
        .partitionBy("customer_id")
        .orderBy(
            F.col("transaction_timestamp").cast("long")
        )
        .rangeBetween(-3600, 0)
    )

    customer_15m = (
        Window
        .partitionBy("customer_id")
        .orderBy(
            F.col("transaction_timestamp").cast("long")
        )
        .rangeBetween(-900, 0)
    )

    card_window = (
        Window
        .partitionBy("customer_id", "card_id")
    )

    merchant_window = (
        Window
        .partitionBy("merchant")
    )

    customer_avg_window = (
        Window
        .partitionBy("customer_id")
    )

    prev_location = F.lag(
        "location"
    ).over(customer_order)

    prev_time = F.lag(
        "transaction_timestamp"
    ).over(customer_order)

    enriched = (
        combined_df

        .withColumn(
            "transaction_timestamp",
            F.to_timestamp("transaction_timestamp")
        )

        .withColumn(
            "previous_location",
            prev_location
        )

        .withColumn(
            "previous_transaction_time",
            prev_time
        )

        .withColumn(
            "minutes_since_previous",
            F.when(
                F.col("previous_transaction_time").isNotNull(),
                (
                    F.unix_timestamp("transaction_timestamp")
                    -
                    F.unix_timestamp("previous_transaction_time")
                ) / 60.0
            ).otherwise(F.lit(None))
        )

        .withColumn(
            "transaction_count_1h",
            F.count("*").over(customer_1h)
        )

        .withColumn(
            "transaction_amount_1h",
            F.sum("amount").over(customer_1h)
        )

        .withColumn(
            "average_transaction_amount",
            F.avg("amount").over(customer_avg_window)
        )

        .withColumn(
            "transactions_per_card",
            F.count("*").over(card_window)
        )

        .withColumn(
            "merchant_frequency",
            F.count("*").over(merchant_window)
        )

        .withColumn(
            "location_change_indicator",
            F.when(
                (
                    F.col("previous_location").isNotNull()
                )
                &
                (
                    F.col("previous_location")
                    != F.col("location")
                )
                &
                (
                    F.col("minutes_since_previous") <= 30
                ),
                1
            ).otherwise(0)
        )

        .withColumn(
            "time_since_previous_transaction",
            F.when(
                F.col("previous_transaction_time").isNotNull(),
                (
                    F.unix_timestamp("transaction_timestamp")
                    -
                    F.unix_timestamp("previous_transaction_time")
                )
            ).otherwise(F.lit(0.0))
        )

        .withColumn(
            "amount_deviation",
            F.when(
                (
                    F.col("average_transaction_amount").isNotNull()
                )
                &
                (
                    F.col("average_transaction_amount") > 0
                ),
                F.abs(
                    F.col("amount")
                    -
                    F.col("average_transaction_amount")
                )
                /
                F.col("average_transaction_amount")
            ).otherwise(F.lit(0.0))
        )

        .withColumn(
            "unusual_hour_indicator",
            F.when(
                F.hour("transaction_timestamp").between(0, 5),
                1
            ).otherwise(0)
        )

        .withColumn(
            "high_amount_indicator",
            F.when(
                (
                    F.col("amount")
                    >=
                    F.coalesce(
                        F.col("avg_spend_per_day"),
                        F.lit(0.0)
                    ) * 3
                )
                |
                (
                    F.col("amount") > 10000
                ),
                1
            ).otherwise(0)
        )

        .withColumn(
            "velocity_flag",
            F.when(
                (
                    F.count("*").over(customer_15m) > 5
                )
                |
                (
                    F.col("transaction_count_1h") > 3
                ),
                1
            ).otherwise(0)
        )

        .withColumn(
            "high_amount_flag",
            F.when(
                F.col("high_amount_indicator") == 1,
                1
            ).otherwise(0)
        )

        .withColumn(
            "location_hop_flag",
            F.when(
                F.col("location_change_indicator") == 1,
                1
            ).otherwise(0)
        )

        .withColumn(
            "unusual_hour_flag",
            F.when(
                F.col("unusual_hour_indicator") == 1,
                1
            ).otherwise(0)
        )

        .withColumn(
            "amount_deviation_flag",
            F.when(
                F.col("amount_deviation") > 1.5,
                1
            ).otherwise(0)
        )

        .withColumn(
            "merchant_frequency_flag",
            F.when(
                F.col("merchant_frequency") > 15,
                1
            ).otherwise(0)
        )
    )

    score_expr = (
        F.when(
            F.col("high_amount_flag") == 1,
            25
        ).otherwise(0)

        +

        F.when(
            F.col("velocity_flag") == 1,
            20
        ).otherwise(0)

        +

        F.when(
            F.col("location_hop_flag") == 1,
            20
        ).otherwise(0)

        +

        F.when(
            F.col("unusual_hour_flag") == 1,
            15
        ).otherwise(0)

        +

        F.when(
            F.col("amount_deviation_flag") == 1,
            20
        ).otherwise(0)

        +

        F.when(
            F.col("merchant_frequency_flag") == 1,
            10
        ).otherwise(0)
    )

    scored = (
        enriched

        .withColumn(
            "risk_score",
            F.greatest(
                F.lit(0.0),
                F.least(
                    F.lit(100.0),
                    score_expr.cast("double")
                )
            )
        )

        .withColumn(
            "risk_level",
            F.when(
                F.col("risk_score") <= 30,
                "LOW"
            )
            .when(
                F.col("risk_score") <= 70,
                "MEDIUM"
            )
            .otherwise("HIGH")
        )

        .withColumn(
            "fraud_rules_triggered",
            F.array(
                F.when(
                    F.col("high_amount_flag") == 1,
                    "high_amount_flag"
                ),

                F.when(
                    F.col("velocity_flag") == 1,
                    "velocity_flag"
                ),

                F.when(
                    F.col("location_hop_flag") == 1,
                    "location_hop_flag"
                ),

                F.when(
                    F.col("unusual_hour_flag") == 1,
                    "unusual_hour_flag"
                ),

                F.when(
                    F.col("amount_deviation_flag") == 1,
                    "amount_deviation_flag"
                ),

                F.when(
                    F.col("merchant_frequency_flag") == 1,
                    "merchant_frequency_flag"
                )
            )
        )

        .withColumn(
            "fraud_rules_triggered",
            F.expr(
                "filter(fraud_rules_triggered, x -> x IS NOT NULL)"
            )
        )

        .withColumn(
            "fraud_prediction",
            F.col("risk_score") >= 71
        )

        .withColumn(
            "processed_at",
            F.current_timestamp()
        )
    )

    features = (
        scored
        .filter(
            F.col("transaction_id").isNotNull()
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
            "processed_at"
        )
        .dropDuplicates(["transaction_id"])
    )

    if not table_exists(features_table):

        (
            features
            .write
            .format("delta")
            .option(
                "delta.enableChangeDataFeed",
                "true"
            )
            .mode("overwrite")
            .saveAsTable(features_table)
        )

    else:

        (
            DeltaTable
            .forName(spark, features_table)
            .alias("t")
            .merge(
                features.alias("s"),
                "t.transaction_id = s.transaction_id"
            )
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )

    high_risk = (
        features
        .filter(
            F.col("fraud_prediction") == True
        )
        .select(
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
            "processed_at"
        )
    )

    if not table_exists(alerts_table):

        (
            high_risk
            .write
            .format("delta")
            .option(
                "delta.enableChangeDataFeed",
                "true"
            )
            .mode("overwrite")
            .saveAsTable(alerts_table)
        )

    elif high_risk.limit(1).count() > 0:

        (
            DeltaTable
            .forName(spark, alerts_table)
            .alias("t")
            .merge(
                high_risk.alias("s"),
                "t.transaction_id = s.transaction_id"
            )
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )

    customer_state = (
        history_df
        .groupBy(
            "customer_id",
            "card_id"
        )
        .agg(
            F.max(
                "transaction_timestamp"
            ).alias("last_transaction_time"),

            F.count("*").alias(
                "transaction_count_30d"
            ),

            F.avg("amount").alias(
                "avg_amount_30d"
            ),

            F.max("amount").alias(
                "max_amount_30d"
            ),

            F.sum("amount").alias(
                "total_amount_30d"
            ),

            F.max_by(
                "location",
                "transaction_timestamp"
            ).alias(
                "last_location"
            )
        )
        .withColumn(
            "updated_at",
            F.current_timestamp()
        )
    )

    if not table_exists(state_table):

        (
            customer_state
            .write
            .format("delta")
            .option(
                "delta.enableChangeDataFeed",
                "true"
            )
            .mode("overwrite")
            .saveAsTable(state_table)
        )

    else:

        (
            DeltaTable
            .forName(spark, state_table)
            .alias("t")
            .merge(
                customer_state.alias("s"),
                """
                t.customer_id = s.customer_id
                AND t.card_id = s.card_id
                """
            )
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )


query = (
    spark
    .readStream
    .table(silver_table)
    .writeStream
    .foreachBatch(process_gold_batch)
    .option(
        "checkpointLocation",
        gold_checkpoint
    )
    .trigger(
        availableNow=True
    )
    .start()
)

query.awaitTermination()

print("========================================")
print("GOLD FRAUD SCORING COMPLETED")
print("========================================")