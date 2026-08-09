

WITH customer_metrics AS (
    SELECT
        c.customer_id,
        c.name,
        c.region,
        COUNT(DISTINCT o.order_id)        AS order_count,
        ROUND(SUM(oi.line_total), 2)      AS total_revenue,
        ROUND(AVG(oi.line_total), 2)      AS avg_order_value,
        MIN(o.order_date)                 AS first_order_date,
        MAX(o.order_date)                 AS last_order_date,
        JULIANDAY(MAX(o.order_date))
            - JULIANDAY(MIN(o.order_date)) AS active_days
    FROM customers c
    JOIN orders o       ON o.customer_id = c.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY c.customer_id
)
SELECT
    customer_id,
    name,
    region,
    order_count,
    avg_order_value,
    total_revenue,
    ROUND(total_revenue / NULLIF(order_count, 0), 2) AS revenue_per_order,
    CAST(active_days AS INTEGER)                     AS active_days,
    ROUND(
        (total_revenue / NULLIF(active_days, 0)) * 365.0,
        2
    )                                                AS projected_annual_value
FROM customer_metrics
ORDER BY total_revenue DESC;