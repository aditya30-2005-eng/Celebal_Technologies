# Fraud scoring rules

This project uses a transparent, deterministic fraud rule engine. Scores are explainable, bounded, and suitable for Databricks SQL dashboards and operational alerting.

Scoring range
-------------
- risk_score: 0 to 100
- risk_level: LOW / MEDIUM / HIGH
- LOW: 0 to 30
- MEDIUM: 31 to 70
- HIGH: 71 to 100

Rule definitions
----------------
1. high_amount_flag
   - trigger: amount is unusually high relative to the customer's normal spend profile or the transaction exceeds a defined high-amount threshold
   - score contribution: +25

2. velocity_flag
   - trigger: multiple transactions in a short window (for example, more than 3 within 1 hour or more than 5 within 15 minutes)
   - score contribution: +20

3. location_hop_flag
   - trigger: the same customer makes a transaction after another transaction in a different location within the allowed time window
   - score contribution: +20

4. unusual_hour_flag
   - trigger: transaction occurs at a high-risk hour such as early morning (e.g., 00:00 to 05:00) or late night
   - score contribution: +15

5. amount_deviation_flag
   - trigger: amount deviates meaningfully from the customer average or rolling transaction mean
   - score contribution: +20

6. merchant_frequency_flag
   - trigger: merchant or category appears abnormally often or is inconsistent with normal buying behavior
   - score contribution: +10

Rule calculation
----------------
The final score is computed by summing the triggered rule contributions and then clamping the result to the 0-100 range.

risk_score = clamp(sum(triggered_rule_weights), 0, 100)

A transaction is flagged for high-risk output when `risk_score >= 71`, which maps to `risk_level='HIGH'`.

Explainability
-------------
Each scored record includes the triggered rules in a list so a reviewer can trace why a score was assigned. This is essential for auditability and avoids using a black-box model when the assignment emphasizes a rule-based approach.

Historical dependency notes
--------------------------
Rules such as `location_hop_flag`, `velocity_flag`, and `amount_deviation_flag` rely on persistent customer and transaction history, not only the current micro-batch. The project maintains this state in Delta tables so that feature calculations stay consistent across stream restarts and across multiple micro-batches.

Limitations
-----------
This is a rules-based engine designed for an assignment and is intentionally explainable. It is not a production fraud model and should be tuned with a larger labeled dataset in a real financial environment.
