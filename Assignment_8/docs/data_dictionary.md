# Data Dictionary

## `customers`

| Column        | Type    | Constraints      | Description                         |
|---------------|---------|------------------|-------------------------------------|
| customer_id   | INTEGER | PK               | Unique customer identifier          |
| name          | TEXT    | NOT NULL         | Customer full name                  |
| email         | TEXT    | UNIQUE, NOT NULL | Email address (must be valid)       |
| region        | TEXT    | NOT NULL         | Geographic region                   |
| city          | TEXT    | NOT NULL         | City of residence                   |
| joined_date   | DATE    | NOT NULL         | Date the customer first registered  |

## `products`

| Column         | Type    | Constraints      | Description                         |
|----------------|---------|------------------|-------------------------------------|
| product_id     | INTEGER | PK               | Unique product identifier           |
| product_name   | TEXT    | NOT NULL         | Display name of the product         |
| category       | TEXT    | NOT NULL         | Product category                    |
| brand          | TEXT    | NOT NULL         | Brand or manufacturer               |
| price          | REAL    | >0               | Current unit price                  |
| stock_quantity | INTEGER | DEFAULT 0        | Units available in inventory        |

## `orders`

| Column          | Type    | Constraints               | Description                           |
|-----------------|---------|---------------------------|---------------------------------------|
| order_id        | INTEGER | PK                        | Unique order identifier               |
| customer_id     | INTEGER | FK → customers, NOT NULL  | Customer who placed the order         |
| order_date      | DATE    | NOT NULL                  | Date the order was placed             |
| status          | TEXT    | NOT NULL, DEFAULT PENDING | Order status                          |
| payment_method  | TEXT    | NOT NULL                  | Payment method used                   |
| shipping_region | TEXT    | NOT NULL                  | Destination region for shipping       |

## `order_items`

| Column         | Type    | Constraints                      | Description                      |
|----------------|---------|----------------------------------|----------------------------------|
| order_item_id  | INTEGER | PK                               | Unique line-item identifier      |
| order_id       | INTEGER | FK → orders, NOT NULL            | Parent order                     |
| product_id     | INTEGER | FK → products, NOT NULL          | Product purchased                |
| quantity       | INTEGER | >= 0, NOT NULL                   | Quantity ordered                 |
| unit_price     | REAL    | NOT NULL                         | Price per unit at order time     |
| discount       | REAL    | DEFAULT 0, BETWEEN 0 AND 1       | Discount fraction applied        |
| line_total     | REAL    | NOT NULL                         | Computed: qty × price × (1-disc) |

## Views

### `customer_summary`

| Column          | Description                                |
|-----------------|--------------------------------------------|
| customer_id     | Customer identifier                        |
| name            | Customer name                              |
| email           | Customer email                             |
| region          | Customer region                            |
| city            | Customer city                              |
| joined_date     | Registration date                          |
| total_orders    | Number of orders placed                    |
| total_spent     | Sum of all line totals                     |
| avg_order_value | Average spend per order                    |
| last_order_date | Date of the most recent order              |

### `product_summary`

| Column              | Description                              |
|---------------------|------------------------------------------|
| product_id          | Product identifier                       |
| product_name        | Product name                             |
| category            | Product category                         |
| brand               | Product brand                            |
| price               | Current unit price                       |
| stock_quantity      | Units in stock                           |
| units_sold          | Number of line items sold                |
| revenue             | Total revenue from this product          |
| total_quantity_sold | Total quantity sold                      |

### `monthly_revenue`

| Column      | Description                             |
|-------------|-----------------------------------------|
| year        | Calendar year                           |
| month       | Calendar month                          |
| month_key   | Padded key for ordering (YYYY-MM)       |
| order_count | Number of orders in the period          |
| revenue     | Total revenue for the period            |

### `top_products`

| Column       | Description                              |
|--------------|------------------------------------------|
| product_id   | Product identifier                       |
| product_name | Product name                             |
| category     | Product category                         |
| units_sold   | Total units sold                         |
| revenue      | Total revenue                            |

