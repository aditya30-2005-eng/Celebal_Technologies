CREATE DATABASE IF NOT EXISTS fraud_db;
USE fraud_db;

CREATE TABLE IF NOT EXISTS fraud_db.bronze_transactions (
  transaction_id STRING,
  customer_id STRING,
  card_id STRING,
  transaction_time STRING,
  amount DOUBLE,
  merchant STRING,
  merchant_category STRING,
  location STRING,
  ingest_timestamp TIMESTAMP,
  source_file STRING,
  raw_record_hash STRING,
  batch_id STRING
)
USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed'='true')
LOCATION '/delta/fraud_db/bronze_transactions';

CREATE TABLE IF NOT EXISTS fraud_db.silver_transactions (
  transaction_id STRING,
  customer_id STRING,
  card_id STRING,
  transaction_timestamp TIMESTAMP,
  transaction_date DATE,
  transaction_hour INT,
  is_weekend BOOLEAN,
  amount DOUBLE,
  merchant STRING,
  merchant_category STRING,
  location STRING,
  home_location STRING,
  avg_spend_per_day DOUBLE,
  preferred_category STRING,
  is_valid BOOLEAN,
  invalid_reasons ARRAY<STRING>,
  data_quality_score DOUBLE,
  ingest_timestamp TIMESTAMP,
  source_file STRING,
  processed_at TIMESTAMP
)
USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed'='true')
LOCATION '/delta/fraud_db/silver_transactions';

CREATE TABLE IF NOT EXISTS fraud_db.silver_rejected_transactions (
  transaction_id STRING,
  customer_id STRING,
  card_id STRING,
  transaction_time STRING,
  amount DOUBLE,
  merchant STRING,
  merchant_category STRING,
  location STRING,
  rejection_reason STRING,
  rejected_at TIMESTAMP,
  source_file STRING
)
USING DELTA
LOCATION '/delta/fraud_db/silver_rejected_transactions';

CREATE TABLE IF NOT EXISTS fraud_db.silver_late_arrivals (
  transaction_id STRING,
  customer_id STRING,
  card_id STRING,
  transaction_timestamp TIMESTAMP,
  amount DOUBLE,
  merchant STRING,
  merchant_category STRING,
  location STRING,
  ingest_timestamp TIMESTAMP,
  source_file STRING,
  reason STRING
)
USING DELTA
LOCATION '/delta/fraud_db/silver_late_arrivals';

CREATE TABLE IF NOT EXISTS fraud_db.gold_transaction_features (
  transaction_id STRING,
  customer_id STRING,
  card_id STRING,
  transaction_timestamp TIMESTAMP,
  amount DOUBLE,
  merchant STRING,
  merchant_category STRING,
  location STRING,
  transaction_count_1h DOUBLE,
  transaction_amount_1h DOUBLE,
  average_transaction_amount DOUBLE,
  amount_deviation DOUBLE,
  transactions_per_card DOUBLE,
  merchant_frequency DOUBLE,
  location_change_indicator INT,
  time_since_previous_transaction DOUBLE,
  unusual_hour_indicator INT,
  high_amount_indicator INT,
  velocity_flag INT,
  high_amount_flag INT,
  location_hop_flag INT,
  unusual_hour_flag INT,
  amount_deviation_flag INT,
  merchant_frequency_flag INT,
  risk_score DOUBLE,
  risk_level STRING,
  fraud_prediction BOOLEAN,
  fraud_rules_triggered ARRAY<STRING>,
  processed_at TIMESTAMP
)
USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed'='true')
LOCATION '/delta/fraud_db/gold_transaction_features';

CREATE TABLE IF NOT EXISTS fraud_db.gold_customer_behavior_state (
  customer_id STRING,
  card_id STRING,
  last_transaction_time TIMESTAMP,
  transaction_count_30d LONG,
  avg_amount_30d DOUBLE,
  max_amount_30d DOUBLE,
  last_location STRING,
  total_amount_30d DOUBLE,
  updated_at TIMESTAMP
)
USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed'='true')
LOCATION '/delta/fraud_db/gold_customer_behavior_state';

CREATE TABLE IF NOT EXISTS fraud_db.gold_high_risk_transactions (
  transaction_id STRING,
  transaction_timestamp TIMESTAMP,
  customer_id STRING,
  card_id STRING,
  amount DOUBLE,
  merchant_id STRING,
  merchant_category STRING,
  location STRING,
  risk_score DOUBLE,
  risk_level STRING,
  fraud_prediction BOOLEAN,
  high_amount_flag INT,
  velocity_flag INT,
  location_hop_flag INT,
  unusual_hour_flag INT,
  amount_deviation_flag INT,
  created_at TIMESTAMP
)
USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed'='true')
LOCATION '/delta/fraud_db/gold_high_risk_transactions';
