

SELECT
    p.category,
    COUNT(oi.order_item_id)                                AS total_items,
    SUM(CASE WHEN o.status = 'RETURNED' THEN 1 ELSE 0 END) AS returned_items,
    ROUND(
        100.0 * SUM(CASE WHEN o.status = 'RETURNED' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(oi.order_item_id), 0),
        2
    )                                                      AS return_rate_pct
FROM order_items oi
JOIN orders o    ON o.order_id = oi.order_id
JOIN products p  ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY return_rate_pct DESC;
