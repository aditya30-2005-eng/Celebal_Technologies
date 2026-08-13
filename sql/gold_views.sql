USE fraud_db;

CREATE OR REPLACE VIEW fraud_db.vw_total_transactions AS
SELECT COUNT(*) AS total_transactions FROM fraud_db.silver_transactions;

CREATE OR REPLACE VIEW fraud_db.vw_total_transaction_amount AS
SELECT ROUND(SUM(amount), 2) AS total_transaction_amount FROM fraud_db.silver_transactions;

CREATE OR REPLACE VIEW fraud_db.vw_fraud_transactions AS
SELECT COUNT(*) AS fraud_transactions FROM fraud_db.gold_transaction_features WHERE fraud_prediction = TRUE;

CREATE OR REPLACE VIEW fraud_db.vw_fraud_percentage AS
SELECT ROUND(100.0 * SUM(CASE WHEN fraud_prediction THEN 1 ELSE 0 END) / COUNT(*), 2) AS fraud_percentage
FROM fraud_db.gold_transaction_features;

CREATE OR REPLACE VIEW fraud_db.vw_fraud_amount AS
SELECT ROUND(SUM(amount), 2) AS fraud_amount
FROM fraud_db.gold_transaction_features WHERE fraud_prediction = TRUE;

CREATE OR REPLACE VIEW fraud_db.vw_high_risk_transactions AS
SELECT COUNT(*) AS high_risk_transactions
FROM fraud_db.gold_high_risk_transactions WHERE risk_level = 'HIGH';

CREATE OR REPLACE VIEW fraud_db.vw_medium_risk_transactions AS
SELECT COUNT(*) AS medium_risk_transactions
FROM fraud_db.gold_high_risk_transactions WHERE risk_level = 'MEDIUM';

CREATE OR REPLACE VIEW fraud_db.vw_low_risk_transactions AS
SELECT COUNT(*) AS low_risk_transactions
FROM fraud_db.gold_high_risk_transactions WHERE risk_level = 'LOW';

CREATE OR REPLACE VIEW fraud_db.vw_risk_score_distribution AS
SELECT risk_level, COUNT(*) AS total_transactions
FROM fraud_db.gold_high_risk_transactions
GROUP BY risk_level
ORDER BY risk_level;

CREATE OR REPLACE VIEW fraud_db.vw_fraud_trend_over_time AS
SELECT CAST(transaction_timestamp AS DATE) AS transaction_day,
       COUNT(*) AS fraud_transactions,
       ROUND(AVG(risk_score), 2) AS avg_risk_score
FROM fraud_db.gold_transaction_features
WHERE fraud_prediction = TRUE
GROUP BY CAST(transaction_timestamp AS DATE)
ORDER BY transaction_day;

CREATE OR REPLACE VIEW fraud_db.vw_top_risky_merchants AS
SELECT merchant AS merchant_name,
       COUNT(*) AS suspicious_count,
       ROUND(AVG(risk_score), 2) AS avg_risk_score
FROM fraud_db.gold_transaction_features
WHERE fraud_prediction = TRUE
GROUP BY merchant
ORDER BY suspicious_count DESC, avg_risk_score DESC;

CREATE OR REPLACE VIEW fraud_db.vw_top_risky_locations AS
SELECT location,
       COUNT(*) AS suspicious_count,
       ROUND(AVG(risk_score), 2) AS avg_risk_score
FROM fraud_db.gold_transaction_features
WHERE fraud_prediction = TRUE
GROUP BY location
ORDER BY suspicious_count DESC, avg_risk_score DESC;

CREATE OR REPLACE VIEW fraud_db.vw_high_risk_transaction_detail AS
SELECT transaction_id,
       transaction_timestamp,
       customer_id,
       card_id,
       amount,
       merchant AS merchant_id,
       merchant_category,
       location,
       risk_score,
       risk_level,
       fraud_prediction
FROM fraud_db.gold_high_risk_transactions
ORDER BY risk_score DESC;

CREATE OR REPLACE VIEW fraud_db.vw_fraud_by_transaction_type AS
SELECT merchant_category AS transaction_type,
       COUNT(*) AS fraud_transactions,
       ROUND(AVG(risk_score), 2) AS avg_risk_score
FROM fraud_db.gold_transaction_features
WHERE fraud_prediction = TRUE
GROUP BY merchant_category
ORDER BY fraud_transactions DESC;

CREATE OR REPLACE VIEW fraud_db.vw_fraud_by_hour AS
SELECT transaction_hour AS hour_of_day,
       COUNT(*) AS fraud_transactions
FROM fraud_db.gold_transaction_features
WHERE fraud_prediction = TRUE
GROUP BY transaction_hour
ORDER BY hour_of_day;
