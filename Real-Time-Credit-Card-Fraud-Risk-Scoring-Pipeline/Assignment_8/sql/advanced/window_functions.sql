

WITH order_history AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_date,
        ROUND(SUM(oi.line_total), 2) AS order_value
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY o.order_id
)
SELECT
    customer_id,
    order_id,
    order_date,
    order_value,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date)  AS row_num,
    RANK()       OVER (PARTITION BY customer_id ORDER BY order_value DESC) AS rank,
    DENSE_RANK() OVER (PARTITION BY customer_id ORDER BY order_value DESC) AS dense_rank,
    LAG(order_value)  OVER (PARTITION BY customer_id ORDER BY order_date)  AS prev_order_value,
    LEAD(order_value) OVER (PARTITION BY customer_id ORDER BY order_date)  AS next_order_value,
    ROUND(SUM(order_value) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS running_customer_total
FROM order_history
ORDER BY customer_id, order_date;
