

WITH monthly_revenue AS (
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
    LAG(revenue) OVER (ORDER BY month_key)                  AS prev_month_revenue,
    ROUND(
        revenue - LAG(revenue) OVER (ORDER BY month_key),
        2
    )                                                       AS change_amount,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY month_key))
        / NULLIF(LAG(revenue) OVER (ORDER BY month_key), 0),
        2
    )                                                       AS change_pct
FROM monthly_revenue
ORDER BY month_key;
