

SELECT
    a.product_id   AS product_a_id,
    a.product_name AS product_a,
    b.product_id   AS product_b_id,
    b.product_name AS product_b,
    COUNT(DISTINCT oi_a.order_id) AS times_bought_together
FROM order_items oi_a
JOIN order_items oi_b
    ON oi_a.order_id = oi_b.order_id
   AND oi_a.product_id <> oi_b.product_id
   AND oi_a.product_id < oi_b.product_id
JOIN products a ON a.product_id = oi_a.product_id
JOIN products b ON b.product_id = oi_b.product_id
GROUP BY a.product_id, b.product_id
ORDER BY times_bought_together DESC
LIMIT 50;