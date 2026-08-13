

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
    LEAD(revenue) OVER (ORDER BY month_key) AS next_month_revenue,
    ROUND(
        LEAD(revenue) OVER (ORDER BY month_key) - revenue,
        2
    )                                      AS projected_change
FROM monthly_revenue
ORDER BY month_key;
