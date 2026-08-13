

SELECT
    strftime('%Y', o.order_date)  AS year,
    strftime('%m', o.order_date)  AS month,
    strftime('%Y-%m', o.order_date) AS month_key,
    COUNT(DISTINCT o.order_id)    AS order_count,
    ROUND(SUM(oi.line_total), 2)  AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
GROUP BY year, month
ORDER BY year, month;
