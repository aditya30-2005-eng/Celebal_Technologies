

SELECT
    c.customer_id,
    c.name,
    c.region,
    COUNT(DISTINCT o.order_id)        AS order_count,
    ROUND(SUM(oi.line_total), 2)      AS total_revenue
FROM customers c
LEFT JOIN orders o       ON o.customer_id = c.customer_id
LEFT JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY c.customer_id
ORDER BY total_revenue DESC;
