

WITH monthly_category AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS month_key,
        p.category,
        ROUND(SUM(oi.line_total), 2)    AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p     ON p.product_id = oi.product_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY strftime('%Y-%m', o.order_date), p.category
),
monthly_average AS (
    SELECT
        month_key,
        ROUND(AVG(revenue), 2) AS avg_category_revenue
    FROM monthly_category
    GROUP BY month_key
)
SELECT
    mc.month_key,
    mc.category,
    mc.revenue,
    ma.avg_category_revenue,
    ROUND(mc.revenue - ma.avg_category_revenue, 2) AS delta_vs_average
FROM monthly_category mc
JOIN monthly_average ma ON ma.month_key = mc.month_key
ORDER BY mc.month_key, mc.revenue DESC;
