

WITH first_purchase AS (
    SELECT
        o.customer_id,
        strftime('%Y-%m', MIN(o.order_date)) AS cohort_month,
        MIN(o.order_date)                     AS first_order_date
    FROM orders o
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY o.customer_id
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS total_customers
    FROM first_purchase
    GROUP BY cohort_month
),
activity AS (
    SELECT DISTINCT
        o.customer_id,
        strftime('%Y-%m', o.order_date) AS activity_month
    FROM orders o
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
)
SELECT
    fp.cohort_month,
    cs.total_customers,
    (
        (CAST(substr(a.activity_month, 1, 4) AS INTEGER) * 12
         + CAST(substr(a.activity_month, 6, 2) AS INTEGER))
        - (CAST(substr(fp.cohort_month, 1, 4) AS INTEGER) * 12
           + CAST(substr(fp.cohort_month, 6, 2) AS INTEGER))
    )                                       AS month_offset,
    COUNT(DISTINCT a.customer_id)           AS active_customers,
    ROUND(
        100.0 * COUNT(DISTINCT a.customer_id)
        / NULLIF(cs.total_customers, 0),
        2
    )                                       AS retention_pct
FROM first_purchase fp
JOIN cohort_size cs ON cs.cohort_month = fp.cohort_month
LEFT JOIN activity a ON a.customer_id = fp.customer_id
GROUP BY fp.cohort_month, month_offset
ORDER BY fp.cohort_month, month_offset;