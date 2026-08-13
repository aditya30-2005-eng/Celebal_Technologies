

WITH customer_spend AS (
    SELECT
        c.customer_id,
        ROUND(SUM(oi.line_total), 2) AS total_spend
    FROM customers c
    JOIN orders o       ON o.customer_id = c.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY c.customer_id
),
tiered AS (
    SELECT
        customer_id,
        total_spend,
        CASE
            WHEN total_spend >= 2000 THEN 'Platinum'
            WHEN total_spend >= 1000 THEN 'Gold'
            WHEN total_spend >= 500  THEN 'Silver'
            ELSE 'Bronze'
        END AS spend_tier
    FROM customer_spend
)
SELECT
    spend_tier,
    COUNT(*)                                   AS customer_count,
    ROUND(SUM(total_spend), 2)                 AS tier_revenue,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS customer_share_pct
FROM tiered
GROUP BY spend_tier
ORDER BY tier_revenue DESC;