

WITH category_revenue AS (
    SELECT
        p.category,
        ROUND(SUM(oi.line_total), 2) AS revenue
    FROM products p
    JOIN order_items oi ON oi.product_id = p.product_id
    JOIN orders o       ON o.order_id = oi.order_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY p.category
)
SELECT
    category,
    revenue,
    DENSE_RANK() OVER (ORDER BY revenue DESC) AS dense_rank
FROM category_revenue
ORDER BY dense_rank;
