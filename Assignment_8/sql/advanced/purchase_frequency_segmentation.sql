

WITH customer_frequency AS (
    SELECT
        c.customer_id,
        c.name,
        COUNT(DISTINCT o.order_id) AS order_count,
        ROUND(SUM(oi.line_total), 2) AS total_revenue
    FROM customers c
    JOIN orders o       ON o.customer_id = c.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY c.customer_id
),
segmented AS (
    SELECT
        customer_id,
        name,
        order_count,
        total_revenue,
        CASE
            WHEN order_count >= 6  THEN 'Loyal'
            WHEN order_count >= 2  THEN 'Occasional'
            WHEN order_count = 1   THEN 'One-Time'
            ELSE 'Inactive'
        END AS frequency_segment
    FROM customer_frequency
)
SELECT
    frequency_segment,
    COUNT(*)                        AS customer_count,
    ROUND(AVG(order_count), 2)      AS avg_orders,
    ROUND(SUM(total_revenue), 2)    AS total_revenue,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS customer_share_pct
FROM segmented
GROUP BY frequency_segment
ORDER BY customer_count DESC;