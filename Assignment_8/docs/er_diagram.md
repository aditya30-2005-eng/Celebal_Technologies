# Entity-Relationship Diagram

```
+------------------+          +------------------+
|    customers     |          |     orders       |
+------------------+          +------------------+
| PK customer_id   |<---------| FK customer_id   |
| name             |  1 : N   | PK order_id      |
| email (UNIQUE)   |          | order_date       |
| region           |          | status           |
| city             |          | payment_method   |
| joined_date      |          | shipping_region  |
+------------------+          +------------------+
                                        |
                                        | 1 : N
                                        |
                               +------------------+
                               |   order_items    |
                               +------------------+
                               | PK order_item_id |
                               | FK order_id      |
                          +----| FK product_id    |
                          |    | quantity         |
                          |    | unit_price       |
                          |    | discount         |
                          |    | line_total       |
                          |    +------------------+
                          |
                          | 1 : N
                          |
               +------------------+
               |    products      |
               +------------------+
               | PK product_id    |
               | product_name     |
               | category         |
               | brand            |
               | price            |
               | stock_quantity   |
               +------------------+
```

## Relationships

| Parent        | Child       | Cardinality | Foreign Key       |
|---------------|-------------|-------------|-------------------|
| `customers`   | `orders`    | 1 : N       | `orders.customer_id` → `customers.customer_id` |
| `orders`      | `order_items` | 1 : N     | `order_items.order_id` → `orders.order_id`     |
| `products`    | `order_items` | 1 : N     | `order_items.product_id` → `products.product_id` |

## Constraints Summary

- `PRIMARY KEY` on every table
- `FOREIGN KEY` references with `ON DELETE CASCADE` and `ON UPDATE CASCADE`
- `NOT NULL` on all entity-descriptive columns
- `UNIQUE` on `customers.email`
- `CHECK` on `order_items.quantity > 0`, `order_items.discount BETWEEN 0 AND 1`,
  `products.price >= 0`, `orders.status` in the allowed status set
- `DEFAULT` values for order status (`PENDING`) and order item discount (`0.0`)

## Indexes

- `idx_orders_customer_id`
- `idx_orders_order_date`
- `idx_orders_status`
- `idx_order_items_order_id`
- `idx_order_items_product`
- `idx_products_category`

