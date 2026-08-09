

WITH ordered_orders AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_date,
        o.status,
        ROW_NUMBER() OVER (
            PARTITION BY o.customer_id
            ORDER BY o.order_date DESC, o.order_id DESC
        ) AS row_num
    FROM orders o
)
SELECT
    customer_id,
    order_id,
    order_date,
    status
FROM ordered_orders
WHERE row_num = 1
ORDER BY customer_id;
