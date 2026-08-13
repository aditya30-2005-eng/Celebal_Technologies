# Architecture and data flow

This project follows a medallion architecture for real-time fraud risk scoring on Databricks. The design emphasizes correctness, explainability, and operational safety rather than speculative or hard-coded logic.

System overview
---------------

The data moves through the following layers:
1. Raw files are ingested into Bronze.
2. Bronze is cleaned and validated in Silver.
3. Gold computes features and risk scores.
4. Dashboard and alert queries read from the Gold tables.

High-level flow
---------------
Raw transaction CSV files -> Bronze Delta table -> Silver Delta table -> Gold feature table -> High-risk output -> Dashboard

Layer responsibilities
---------------------
Bronze
- accept raw ingestion from a source directory
- preserve the original payload
- capture source metadata and ingestion timestamps
- prevent duplicate raws using deterministic hashing and Delta MERGE

Silver
- cast timestamps and numeric values correctly
- reject invalid records with clear reasons
- standardize categories and locations
- join profile context from customer baseline data
- store valid records separately from rejected rows
- write stateful business-ready rows with data quality indicators

Gold
- compute rollups, historical features, and customer behavior state
- produce explainable fraud scores
- create a final high-risk table for operational review and database alerts

Streaming flow
--------------
The project uses PySpark Structured Streaming with Delta as the sink. The Bronze stream reads incoming CSV files from a directory and writes to Delta. The Silver layer reads from Bronze in micro-batches, validates records, and writes valid and rejected outputs. The Gold layer reads historical Silver data plus the current batch to create rolling features and customer-state updates.

Historical state handling
-------------------------
Historical state is maintained through Delta tables, not through per-micro-batch memory alone. The main persistent state tables are:
- `fraud_db.silver_transactions` (valid transaction history)
- `fraud_db.gold_customer_behavior_state` (customer/card behavior state)
- `fraud_db.gold_transaction_features` (history of computed features per transaction)

When a new batch arrives, the pipeline reads the historical tables and derives features such as prior location, rolling counts, average amount, and prior transaction gaps. This means feature calculations are not reset at each micro-batch. Checkpointing ensures the stream can resume without re-reading all historical data from scratch.

Late-arriving data handling
---------------------------
Late-arriving transactions are handled using `withWatermark()` on `transaction_timestamp` and a watermarked processing window. Records older than the allowed lateness threshold are not silently discarded; they are routed to `fraud_db.silver_late_arrivals` with the reason for late arrival recorded in the processing logic. This is important because a naive stream may incorrectly include stale rows in rolling windows.

Risk scoring flow
-----------------
Gold computes explainable features such as:
- transaction_count_1h
- transaction_amount_1h
- average_transaction_amount
- amount_deviation
- transactions_per_card
- merchant_frequency
- location_change_indicator
- time_since_previous_transaction
- unusual_hour_indicator
- high_amount_indicator

These features are converted into rule indicators and a risk score from 0 to 100.

Data quality rules
------------------
A row is considered valid only when:
- `transaction_id` is present
- `customer_id` and `card_id` are present
- `amount` is positive
- `transaction_time` is valid and not in the future
- required categorical values are present
- no duplicate key issue remains after dedupe

Invalid rows are captured in `fraud_db.silver_rejected_transactions` with a rejection reason list.

Operational constraints and limitations
--------------------------------------
- The repo is built for Databricks; local execution is limited to static validation only.
- Actual streaming execution, checkpoint correctness, and cloud path behavior need a live Databricks cluster.
- Production systems should also add monitoring, alert thresholds, and data retention logic.

Delta Lake and checkpointing
---------------------------
Delta tables provide ACID semantics and reliable merge logic for idempotent writes. Checkpoint locations keep stream progress durable across restarts so a job can resume without duplicating or losing updates.
