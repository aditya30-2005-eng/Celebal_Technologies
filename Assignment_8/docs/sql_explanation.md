# SQL Analytics Explained

All queries live under `sql/` and execute against the SQLite database built
from `sql/schema.sql`. Tables are `customers` (c), `products` (p), `orders`
(o), and `order_items` (oi).

## Basic

| Query                     | File                                 | What it answers                                   |
|---------------------------|--------------------------------------|----------------------------------------------------|
| Revenue by category       | `basic/revenue_by_category.sql`      | Total revenue, orders, and items per category      |
| Revenue by customer       | `basic/revenue_by_customer.sql`      | Lifetime spend and order counts per customer       |
| Revenue by month          | `basic/revenue_by_month.sql`         | Monthly order count and revenue time series        |
| Top 10 customers          | `basic/top_customers.sql`            | Highest-spending customers with rank               |
| Top products              | `basic/top_products.sql`             | Best-selling products by units and revenue         |

## Intermediate

| Query                            | File                                      | What it answers                                  |
|----------------------------------|-------------------------------------------|---------------------------------------------------|
| Never delivered customers        | `intermediate/never_delivered.sql`        | Customers with no delivered order                 |
| Return rate                      | `intermediate/return_rate.sql`            | Returned fraction per product                     |
| Products returned more than sold | `intermediate/products_returned_more_than_sold.sql` | Products where returns exceed sales    |

## Advanced (window functions and CTEs)

| Query                   | Technique                         | Purpose                                    |
|-------------------------|-----------------------------------|---------------------------------------------|
| Running total           | `SUM() OVER (ROWS)`               | Cumulative revenue over time                |
| Moving average          | `AVG() OVER (ROWS BETWEEN ...)`   | 3-month smoothed revenue trend              |
| Dense rank              | `DENSE_RANK() OVER`               | Sequential ranks without gaps by revenue    |
| Rank                    | `RANK() OVER`                     | Revenue ranks with ties                     |
| Row number              | `ROW_NUMBER() OVER`               | Ordering rows within a partition            |
| Lag                     | `LAG() OVER`                      | Previous month value                       |
| Lead                    | `LEAD() OVER`                     | Next month value                            |
| Window functions        | Combined window set                | Wide analytical view of revenue             |
| Nested CTE              | `WITH ... AS (SELECT ...)`         | Chained sub-queries for staging              |
| Multi-level CTE         | Multiple stacked CTEs              | Complex derived datasets                     |
| Year-over-year          | `LAG()` on year                        | Year revenue deltas and percentages          |
| NTILE                  | `NTILE(4) OVER`                     | Quartile bands of customers                  |
| Quartiles               | `ROW_NUMBER()` + `COUNT(*)`       | Q1 / median / Q3 of order values            |
| First/Last value        | `FIRST_VALUE() / LAST_VALUE()`     | Boundary values in a window                  |
| Cumulative distribution | `CUME_DIST()` OVER                | Relative standing of each customer           |
| Self join               | `order_items` joined to itself      | Same-category products bought together       |
| Cohort analysis         | First-purchase month cohorts       | Cohort size and activity month retention     |
| Retention               | Cohort × month-offset matrix       | Retention percentage per cohort              |
| Customer lifetime value | Monetary value + lifespan          | Long-term customer worth                     |
| RFM                    | R/F/M score + combined cell        | Recency, frequency, monetary quintiles       |
| Segmentation            | Score-based segment labels         | Business-friendly customer cohorts           |
| Spend tier              | Revenue boundaries                 | Platinum / Gold / Silver / Bronze bands       |
| Frequency tier          | Order-count boundaries             | Very Frequent / Frequent / Occasional etc.   |
| Repeat customers        | Single vs repeat classification    | Share of revenue from repeat buyers          |
| Churn detection         | Days-inactive thresholds            | Active / At Risk / Churned flags             |

```sql
-- Example: running total of revenue by month
SELECT
    oi.line_total,
    SUM(oi.line_total) OVER (ORDER BY o.order_date) AS running_total
FROM order_items oi
JOIN orders o USING (order_id);
```

