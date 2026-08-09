

SELECT
    c.customer_id,
    c.name,
    c.email,
    COUNT(o.order_id)                          AS undelivered_orders,
    MAX(o.order_date)                          AS last_order_date,
    GROUP_CONCAT(DISTINCT o.status)            AS statuses
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE c.customer_id NOT IN (
    SELECT DISTINCT customer_id
    FROM orders
    WHERE status = 'DELIVERED'
)
GROUP BY c.customer_id
ORDER BY undelivered_orders DESC;
