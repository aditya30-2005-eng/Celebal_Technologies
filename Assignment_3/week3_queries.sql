CREATE DATABASE IF NOT EXISTS week3_sales;
USE week3_sales;

SELECT * FROM `sample - superstore` LIMIT 10;

DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;

CREATE TABLE customers AS
SELECT DISTINCT
    `Customer ID`,
    `Customer Name`,
    Segment
FROM `sample - superstore`;

CREATE TABLE orders AS
SELECT DISTINCT
    `Order ID`,
    `Order Date`,
    `Ship Date`,
    `Ship Mode`,
    `Customer ID`,
    Sales
FROM `sample - superstore`;

CREATE TABLE products AS
SELECT DISTINCT
    `Product ID`,
    Category,
    `Sub-Category`,
    `Product Name`
FROM `sample - superstore`;

-- Q1
SELECT *
FROM orders
WHERE Sales > (
    SELECT AVG(Sales)
    FROM orders
);

-- Q2
SELECT `Customer ID`,
MAX(Sales) AS highest_sale
FROM orders
GROUP BY `Customer ID`;

-- Q3
WITH customer_sales AS (
    SELECT `Customer ID`,
    SUM(Sales) AS total_sales
    FROM orders
    GROUP BY `Customer ID`
)
SELECT * FROM customer_sales;

-- Q4
WITH customer_sales AS (
    SELECT `Customer ID`,
    SUM(Sales) AS total_sales
    FROM orders
    GROUP BY `Customer ID`
)
SELECT *
FROM customer_sales
WHERE total_sales > (
    SELECT AVG(total_sales)
    FROM customer_sales
);

-- Q5
SELECT `Customer ID`,
SUM(Sales) AS total_sales,
RANK() OVER (ORDER BY SUM(Sales) DESC) AS ranking
FROM orders
GROUP BY `Customer ID`;

-- Q6
SELECT `Customer ID`,
`Order ID`,
Sales,
ROW_NUMBER() OVER (
    PARTITION BY `Customer ID`
    ORDER BY Sales DESC
) AS row_num
FROM orders;

-- Q7
SELECT *
FROM (
    SELECT `Customer ID`,
    SUM(Sales) AS total_sales,
    RANK() OVER (ORDER BY SUM(Sales) DESC) AS ranking
    FROM orders
    GROUP BY `Customer ID`
) ranked
WHERE ranking <= 3;

-- Final Combined Query
WITH customer_sales AS (
    SELECT `Customer ID`,
    SUM(Sales) AS total_sales
    FROM orders
    GROUP BY `Customer ID`
)
SELECT c.`Customer Name`,
cs.total_sales,
RANK() OVER (ORDER BY cs.total_sales DESC) AS ranking
FROM customer_sales cs
JOIN customers c
ON cs.`Customer ID` = c.`Customer ID`;

-- Mini Project Q1: Top 5 customers
SELECT `Customer ID`,
SUM(Sales) AS total_sales
FROM orders
GROUP BY `Customer ID`
ORDER BY total_sales DESC
LIMIT 5;

-- Mini Project Q2: Bottom 5 customers
SELECT `Customer ID`,
SUM(Sales) AS total_sales
FROM orders
GROUP BY `Customer ID`
ORDER BY total_sales ASC
LIMIT 5;

-- Mini Project Q3: Single order customers
SELECT `Customer ID`,
COUNT(`Order ID`) AS total_orders
FROM orders
GROUP BY `Customer ID`
HAVING COUNT(`Order ID`) = 1;

-- Mini Project Q4: Above-average sales customers
WITH customer_sales AS (
    SELECT `Customer ID`,
    SUM(Sales) AS total_sales
    FROM orders
    GROUP BY `Customer ID`
)
SELECT *
FROM customer_sales
WHERE total_sales > (
    SELECT AVG(total_sales)
    FROM customer_sales
);

-- Mini Project Q5: Highest order value per customer
SELECT `Customer ID`,
`Order ID`,
Sales
FROM (
    SELECT `Customer ID`,
           `Order ID`,
           Sales,
           ROW_NUMBER() OVER (
               PARTITION BY `Customer ID`
               ORDER BY Sales DESC
           ) AS rn
    FROM orders
) ranked_orders
WHERE rn = 1;