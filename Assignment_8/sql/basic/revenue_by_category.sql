

SELECT
    p.category,
    COUNT(DISTINCT o.order_id)            AS order_count,
    COUNT(oi.order_item_id)               AS item_count,
    ROUND(SUM(oi.line_total), 2)          AS revenue,
    ROUND(AVG(oi.line_total), 2)          AS avg_line_value
FROM products p
JOIN order_items oi ON oi.product_id = p.product_id
JOIN orders o       ON o.order_id = oi.order_id
WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
GROUP BY p.category
ORDER BY revenue DESC;
