

WITH yearly_revenue AS (
    SELECT
        strftime('%Y', o.order_date) AS year,
        ROUND(SUM(oi.line_total), 2) AS total_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY strftime('%Y', o.order_date)
),
category_by_year AS (
    SELECT
        strftime('%Y', o.order_date) AS year,
        p.category,
        ROUND(SUM(oi.line_total), 2) AS category_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p     ON p.product_id = oi.product_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY strftime('%Y', o.order_date), p.category
)
SELECT
    cy.year,
    cy.category,
    cy.category_revenue,
    yr.total_revenue,
    ROUND(100.0 * cy.category_revenue / NULLIF(yr.total_revenue, 0), 2) AS share_pct
FROM category_by_year cy
JOIN yearly_revenue yr ON yr.year = cy.year
ORDER BY cy.year, cy.category_revenue DESC;
