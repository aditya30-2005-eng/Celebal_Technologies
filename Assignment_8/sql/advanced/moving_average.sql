

WITH monthly AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS month_key,
        ROUND(SUM(oi.line_total), 2)    AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY strftime('%Y-%m', o.order_date)
)
SELECT
    month_key,
    revenue,
    ROUND(
        AVG(revenue) OVER (
            ORDER BY month_key
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS moving_avg_3m
FROM monthly
ORDER BY month_key;
