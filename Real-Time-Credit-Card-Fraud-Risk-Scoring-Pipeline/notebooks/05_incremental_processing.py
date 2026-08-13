from __future__ import annotations

from delta.tables import DeltaTable
from pyspark.sql import functions as F

SILVER_TABLE = "fraud_db.silver_transactions"


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


def latest_silver_version():
    if not table_exists(SILVER_TABLE):
        return None

    delta_table = DeltaTable.forName(
        spark,
        SILVER_TABLE
    )

    history = (
        delta_table
        .history()
        .select("version")
        .orderBy(F.col("version").desc())
        .limit(1)
        .collect()
    )

    if not history:
        return None

    return history[0]["version"]


def read_cdf_between(start_version: int, end_version: int):
    return (
        spark.read
        .format("delta")
        .option("readChangeFeed", "true")
        .option("startingVersion", start_version)
        .option("endingVersion", end_version)
        .table(SILVER_TABLE)
    )


print("========================================")
print("INCREMENTAL PROCESSING")
print("========================================")


if not table_exists(SILVER_TABLE):

    print("Silver table does not exist.")
    print("Run the Silver pipeline first.")

else:

    current_version = latest_silver_version()

    print(f"Latest Silver Delta version: {current_version}")

    if current_version is None:

        print("Silver table has no Delta history.")

    else:

        print("Reading latest Delta Change Data Feed...")

        try:

            cdf_df = read_cdf_between(
                current_version,
                current_version
            )

            cdf_count = cdf_df.count()

            print(f"CDF records found: {cdf_count}")

            if cdf_count > 0:

                print("Change Data Feed summary:")

                display(
                    cdf_df.groupBy("_change_type")
                    .count()
                    .orderBy("_change_type")
                )

                print("Latest incremental records:")

                display(
                    cdf_df
                    .orderBy(
                        F.col("_commit_version").desc()
                    )
                    .limit(20)
                )

            else:

                print("No changes found in the latest version.")

        except Exception as e:

            print("CDF could not be read.")
            print(str(e))

            print()
            print("Trying normal incremental table read...")

            display(
                spark.table(SILVER_TABLE)
                .orderBy(
                    F.col("processed_at").desc()
                )
                .limit(20)
            )


print("========================================")
print("INCREMENTAL PROCESSING COMPLETED")
print("========================================")