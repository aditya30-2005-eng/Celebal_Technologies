

WITH cohort_definition AS (
    SELECT
        c.customer_id,
        strftime('%Y-%m', c.joined_date) AS cohort_month,
        c.joined_date
    FROM customers c
),
activity AS (
    SELECT DISTINCT
        c.customer_id,
        strftime('%Y-%m', o.order_date) AS activity_month
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS size
    FROM cohort_definition
    GROUP BY cohort_month
)
SELECT
    cd.cohort_month,
    a.activity_month,
    cs.size                                          AS cohort_size,
    COUNT(DISTINCT a.customer_id)                    AS active_customers,
    ROUND(
        100.0 * COUNT(DISTINCT a.customer_id) / NULLIF(cs.size, 0),
        2
    )                                                AS retention_pct
FROM cohort_definition cd
JOIN activity a   ON a.customer_id = cd.customer_id
JOIN cohort_size cs ON cs.cohort_month = cd.cohort_month
GROUP BY cd.cohort_month, a.activity_month
ORDER BY cd.cohort_month, a.activity_month;