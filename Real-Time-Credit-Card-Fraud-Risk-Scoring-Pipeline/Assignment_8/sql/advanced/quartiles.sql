

WITH order_values AS (
    SELECT
        o.order_id,
        ROUND(SUM(oi.line_total), 2) AS order_value
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY o.order_id
),
ranked AS (
    SELECT
        order_value,
        ROW_NUMBER() OVER (ORDER BY order_value) AS row_num,
        COUNT(*) OVER ()                         AS total_rows
    FROM order_values
),
quartile_values AS (
    SELECT
        MAX(CASE WHEN row_num <= total_rows * 0.25 THEN order_value END) AS q1,
        MAX(CASE WHEN row_num <= total_rows * 0.50 THEN order_value END) AS q2,
        MAX(CASE WHEN row_num <= total_rows * 0.75 THEN order_value END) AS q3
    FROM ranked
)
SELECT
    ROUND(q1, 2) AS q1,
    ROUND(q2, 2) AS median,
    ROUND(q3, 2) AS q3,
    ROUND(q3 - q1, 2) AS interquartile_range
FROM quartile_values;