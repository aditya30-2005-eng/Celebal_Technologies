

WITH last_activity AS (
    SELECT
        c.customer_id,
        c.name,
        c.region,
        MAX(o.order_date)                        AS last_order_date,
        JULIANDAY('now') - JULIANDAY(MAX(o.order_date)) AS days_since_last_order,
        COUNT(DISTINCT o.order_id)               AS order_count
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY c.customer_id
)
SELECT
    customer_id,
    name,
    region,
    last_order_date,
    CAST(days_since_last_order AS INTEGER) AS days_inactive,
    CASE
        WHEN days_since_last_order > 365 THEN 'Churned - Long Term'
        WHEN days_since_last_order > 180 THEN 'Churned'
        WHEN days_since_last_order > 90  THEN 'At Risk'
        WHEN days_since_last_order > 30  THEN 'Slipping'
        ELSE 'Active'
    END                                     AS churn_status,
    order_count
FROM last_activity
ORDER BY days_since_last_order DESC;