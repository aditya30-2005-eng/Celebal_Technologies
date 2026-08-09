

WITH customer_revenue AS (
    SELECT
        c.customer_id,
        c.name,
        c.region,
        ROUND(SUM(oi.line_total), 2) AS revenue
    FROM customers c
    JOIN orders o       ON o.customer_id = c.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY c.customer_id, c.region
)
SELECT
    customer_id,
    name,
    region,
    revenue,
    RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS rank_in_region
FROM customer_revenue
ORDER BY region, rank_in_region;
