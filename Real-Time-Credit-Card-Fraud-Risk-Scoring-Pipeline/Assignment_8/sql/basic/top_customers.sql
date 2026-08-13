

WITH customer_revenue AS (
    SELECT
        c.customer_id,
        c.name,
        c.region,
        ROUND(SUM(oi.line_total), 2) AS total_revenue,
        COUNT(DISTINCT o.order_id)   AS order_count
    FROM customers c
    JOIN orders o       ON o.customer_id = c.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY c.customer_id
)
SELECT
    DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS rank,
    customer_id,
    name,
    region,
    order_count,
    total_revenue
FROM customer_revenue
ORDER BY total_revenue DESC
LIMIT 10;
