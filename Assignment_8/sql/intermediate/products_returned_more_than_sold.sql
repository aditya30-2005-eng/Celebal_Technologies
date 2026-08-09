

WITH sales_by_product AS (
    SELECT
        oi.product_id,
        COUNT(oi.order_item_id) AS sold_items,
        SUM(CASE WHEN o.status = 'RETURNED' THEN 1 ELSE 0 END) AS returned_items
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    GROUP BY oi.product_id
)
SELECT
    p.product_id,
    p.product_name,
    p.category,
    s.sold_items,
    s.returned_items,
    ROUND(100.0 * s.returned_items / NULLIF(s.sold_items, 0), 2) AS return_pct
FROM sales_by_product s
JOIN products p ON p.product_id = s.product_id
WHERE s.returned_items > s.sold_items
ORDER BY s.returned_items DESC;
