

WITH monthly_revenue AS (
    SELECT
        CAST(strftime('%Y', o.order_date) AS INTEGER) AS year,
        CAST(strftime('%m', o.order_date) AS INTEGER) AS month,
        ROUND(SUM(oi.line_total), 2)                  AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY year, month
)
SELECT
    current.year,
    current.month,
    current.revenue                                        AS current_revenue,
    prior.revenue                                          AS prior_year_revenue,
    ROUND(current.revenue - prior.revenue, 2)              AS absolute_change,
    ROUND(
        100.0 * (current.revenue - prior.revenue)
        / NULLIF(prior.revenue, 0),
        2
    )                                                      AS change_pct
FROM monthly_revenue current
LEFT JOIN monthly_revenue prior
    ON prior.year = current.year - 1
   AND prior.month = current.month
ORDER BY current.year, current.month;
