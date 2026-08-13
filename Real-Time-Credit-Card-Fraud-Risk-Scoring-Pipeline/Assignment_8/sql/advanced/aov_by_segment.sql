

WITH customer_rfm AS (
    SELECT
        c.customer_id,
        JULIANDAY('now') - JULIANDAY(MAX(o.order_date)) AS recency_days,
        COUNT(DISTINCT o.order_id)                       AS frequency,
        ROUND(SUM(oi.line_total), 2)                     AS monetary
    FROM customers c
    JOIN orders o       ON o.customer_id = c.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY c.customer_id
),
scored AS (
    SELECT
        customer_id,
        recency_days,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency)         AS f_score,
        NTILE(5) OVER (ORDER BY monetary)          AS m_score
    FROM customer_rfm
),
segmented AS (
    SELECT
        customer_id,
        frequency,
        monetary,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 2 AND m_score <= 2 THEN 'New Customers'
            WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            WHEN m_score >= 4 AND r_score <= 2 THEN 'Big Spenders At Risk'
            ELSE 'Promising'
        END AS segment
    FROM scored
)
SELECT
    segment,
    COUNT(*)                        AS customer_count,
    SUM(frequency)                  AS total_orders,
    ROUND(SUM(monetary), 2)         AS total_revenue,
    ROUND(SUM(monetary) / NULLIF(SUM(frequency), 0), 2) AS average_order_value
FROM segmented
GROUP BY segment
ORDER BY total_revenue DESC;