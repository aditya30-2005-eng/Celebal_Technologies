USE fraud_db;

SELECT 'bronze_transactions' AS table_name, COUNT(*) AS row_count FROM fraud_db.bronze_transactions
UNION ALL
SELECT 'silver_transactions', COUNT(*) FROM fraud_db.silver_transactions
UNION ALL
SELECT 'silver_rejected_transactions', COUNT(*) FROM fraud_db.silver_rejected_transactions
UNION ALL
SELECT 'silver_late_arrivals', COUNT(*) FROM fraud_db.silver_late_arrivals
UNION ALL
SELECT 'gold_transaction_features', COUNT(*) FROM fraud_db.gold_transaction_features
UNION ALL
SELECT 'gold_high_risk_transactions', COUNT(*) FROM fraud_db.gold_high_risk_transactions;

SELECT transaction_id, COUNT(*) AS cnt
FROM fraud_db.silver_transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;

SELECT COUNT(*) AS invalid_records
FROM fraud_db.silver_transactions
WHERE transaction_id IS NULL
   OR customer_id IS NULL
   OR card_id IS NULL
   OR amount IS NULL
   OR amount <= 0
   OR transaction_timestamp IS NULL;

SELECT COUNT(*) AS rejected_records
FROM fraud_db.silver_rejected_transactions;

SELECT MIN(risk_score) AS min_risk_score,
       MAX(risk_score) AS max_risk_score,
       AVG(risk_score) AS avg_risk_score
FROM fraud_db.gold_transaction_features;

SELECT COUNT(*) AS low_risk_rows
FROM fraud_db.gold_transaction_features
WHERE risk_level = 'LOW';

SELECT COUNT(*) AS medium_risk_rows
FROM fraud_db.gold_transaction_features
WHERE risk_level = 'MEDIUM';

SELECT COUNT(*) AS high_risk_rows
FROM fraud_db.gold_transaction_features
WHERE risk_level = 'HIGH';

SELECT COUNT(*) AS out_of_range_rows
FROM fraud_db.gold_transaction_features
WHERE risk_score < 0 OR risk_score > 100;

SELECT COUNT(*) AS late_records
FROM fraud_db.silver_late_arrivals;

SELECT merchant_category,
       COUNT(*) AS fraud_rows
FROM fraud_db.gold_transaction_features
WHERE fraud_prediction = TRUE
GROUP BY merchant_category
ORDER BY fraud_rows DESC;
