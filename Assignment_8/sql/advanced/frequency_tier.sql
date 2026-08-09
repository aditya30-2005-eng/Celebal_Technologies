

WITH customer_frequency AS (
    SELECT
        c.customer_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY c.customer_id
),
tiered AS (
    SELECT
        customer_id,
        order_count,
        CASE
            WHEN order_count >= 20 THEN 'Very Frequent'
            WHEN order_count >= 10 THEN 'Frequent'
            WHEN order_count >= 5  THEN 'Occasional'
            WHEN order_count >= 1  THEN 'New'
            ELSE 'Inactive'
        END AS frequency_tier
    FROM customer_frequency
)
SELECT
    frequency_tier,
    COUNT(*) AS customer_count,
    ROUND(AVG(order_count), 2) AS avg_orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct
FROM tiered
GROUP BY frequency_tier
ORDER BY customer_count DESC;