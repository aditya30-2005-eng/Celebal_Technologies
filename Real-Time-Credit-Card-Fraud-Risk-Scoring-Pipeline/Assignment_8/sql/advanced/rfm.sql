

WITH customer_rfm AS (
    SELECT
        c.customer_id,
        c.name,
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
        name,
        recency_days,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency)         AS f_score,
        NTILE(5) OVER (ORDER BY monetary)          AS m_score
    FROM customer_rfm
)
SELECT
    customer_id,
    name,
    CAST(recency_days AS INTEGER)      AS recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    r_score || f_score || m_score      AS rfm_cell,
    r_score + f_score + m_score        AS rfm_total
FROM scored
ORDER BY rfm_total DESC;