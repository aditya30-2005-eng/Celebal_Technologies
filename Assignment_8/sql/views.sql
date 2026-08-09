

DROP VIEW IF EXISTS customer_summary;
CREATE VIEW customer_summary AS
SELECT
    c.customer_id,
    c.name,
    c.email,
    c.region,
    c.city,
    c.joined_date,
    COUNT(DISTINCT o.order_id)                    AS total_orders,
    COALESCE(SUM(oi.line_total), 0)               AS total_spent,
    COALESCE(AVG(oi.line_total), 0)               AS avg_order_value,
    MAX(o.order_date)                             AS last_order_date
FROM customers c
LEFT JOIN orders o       ON o.customer_id = c.customer_id
LEFT JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY c.customer_id;

DROP VIEW IF EXISTS product_summary;
CREATE VIEW product_summary AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    p.price,
    p.stock_quantity,
    COUNT(oi.order_item_id)                AS units_sold,
    COALESCE(SUM(oi.line_total), 0)        AS revenue,
    COALESCE(SUM(oi.quantity), 0)          AS total_quantity_sold
FROM products p
LEFT JOIN order_items oi ON oi.product_id = p.product_id
GROUP BY p.product_id;

DROP VIEW IF EXISTS monthly_revenue;
CREATE VIEW monthly_revenue AS
SELECT
    strftime('%Y', o.order_date) AS year,
    strftime('%m', o.order_date) AS month,
    strftime('%Y-%m', o.order_date) AS month_key,
    COUNT(DISTINCT o.order_id)   AS order_count,
    COALESCE(SUM(oi.line_total), 0) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status IN ('DELIVERED', 'SHIPPED', 'PROCESSING')
GROUP BY year, month
ORDER BY year, month;

DROP VIEW IF EXISTS top_products;
CREATE VIEW top_products AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    COALESCE(SUM(oi.quantity), 0)  AS units_sold,
    COALESCE(SUM(oi.line_total), 0) AS revenue
FROM products p
JOIN order_items oi ON oi.product_id = p.product_id
GROUP BY p.product_id
ORDER BY revenue DESC;
