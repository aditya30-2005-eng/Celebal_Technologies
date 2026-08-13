

SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    SUM(oi.quantity)         AS units_sold,
    ROUND(SUM(oi.line_total), 2) AS revenue,
    RANK() OVER (ORDER BY SUM(oi.line_total) DESC) AS revenue_rank
FROM products p
JOIN order_items oi ON oi.product_id = p.product_id
JOIN orders o       ON o.order_id = oi.order_id
WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 25;
