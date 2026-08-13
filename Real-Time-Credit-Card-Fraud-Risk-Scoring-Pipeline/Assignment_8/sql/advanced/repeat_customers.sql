

WITH customer_orders AS (
    SELECT
        c.customer_id,
        c.name,
        COUNT(DISTINCT o.order_id)   AS order_count,
        ROUND(SUM(oi.line_total), 2) AS revenue
    FROM customers c
    JOIN orders o       ON o.customer_id = c.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY c.customer_id
)
SELECT
    CASE
        WHEN order_count = 1 THEN 'Single Purchase'
        ELSE 'Repeat Customer'
    END                                          AS customer_type,
    COUNT(*)                                     AS customer_count,
    ROUND(SUM(revenue), 2)                       AS total_revenue,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS customer_share_pct,
    ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 2) AS revenue_share_pct
FROM customer_orders
GROUP BY customer_type
ORDER BY total_revenue DESC;