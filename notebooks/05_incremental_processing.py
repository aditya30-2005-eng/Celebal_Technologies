from __future__ import annotations

from delta.tables import DeltaTable

silver_table = "fraud_db.silver_transactions"


def read_cdf_between(start_version: int, end_version: int):
    return (
        spark.read.format("delta")
        .option("readChangeFeed", "true")
        .option("startingVersion", start_version)
        .option("endingVersion", end_version)
        .table(silver_table)
    )


def latest_silver_version():
    delta_table = DeltaTable.forName(spark, silver_table)
    history = delta_table.history(1).collect()
    return history[0].version if history else None


print("Incremental processing helper loaded. CDF is optional for this assignment and is used only when a Delta table is actively updated.")
