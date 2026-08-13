

SELECT
    strftime('%Y-%m', o.order_date)              AS month_key,
    ROUND(SUM(oi.line_total), 2)                 AS monthly_revenue,
    ROUND(SUM(SUM(oi.line_total)) OVER (ORDER BY strftime('%Y-%m', o.order_date)), 2)
                                                 AS running_total
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
GROUP BY strftime('%Y-%m', o.order_date)
ORDER BY month_key;
