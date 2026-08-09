

WITH customer_spend AS (
    SELECT
        c.customer_id,
        c.name,
        ROUND(SUM(oi.line_total), 2) AS total_spend
    FROM customers c
    JOIN orders o       ON o.customer_id = c.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY c.customer_id
)
SELECT
    customer_id,
    name,
    total_spend,
    ROUND(CUME_DIST() OVER (ORDER BY total_spend DESC), 4) AS cum_distribution
FROM customer_spend
ORDER BY total_spend DESC;
