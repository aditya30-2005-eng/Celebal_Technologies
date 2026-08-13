

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    customer_name   TEXT    NOT NULL DEFAULT '',
    email           TEXT    NOT NULL UNIQUE,
    customer_type   TEXT    NOT NULL DEFAULT 'REGULAR',
    region          TEXT    NOT NULL DEFAULT 'Unknown',
    city            TEXT    NOT NULL DEFAULT 'Unknown',
    joined_date     DATE    NOT NULL DEFAULT (date('now')),
    registration_date DATE NOT NULL DEFAULT (date('now')),
    CHECK (length(trim(email)) > 5 AND instr(email, '@') > 0)
);

CREATE TABLE products (
    product_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name   TEXT    NOT NULL,
    category       TEXT    NOT NULL DEFAULT 'Uncategorized',
    subcategory    TEXT    NOT NULL DEFAULT 'General',
    brand          TEXT    NOT NULL DEFAULT 'Unknown',
    price          REAL    NOT NULL DEFAULT 0.0
        CHECK (price >= 0),
    cost_price     REAL    NOT NULL DEFAULT 0.0
        CHECK (cost_price >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0
        CHECK (stock_quantity >= 0)
);

CREATE TABLE orders (
    order_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL,
    order_date      DATE    NOT NULL DEFAULT (date('now')),
    status          TEXT    NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'PROCESSING', 'SHIPPED',
                          'DELIVERED', 'CANCELLED', 'RETURNED', 'REFUNDED')),
    payment_method  TEXT    NOT NULL DEFAULT 'unknown',
    shipping_region TEXT    NOT NULL DEFAULT 'Unknown',
    region_code     TEXT    NOT NULL DEFAULT 'Unknown',
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE order_items (
    order_item_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id          INTEGER NOT NULL DEFAULT 0,
    order_id         INTEGER NOT NULL,
    product_id       INTEGER NOT NULL,
    quantity         INTEGER NOT NULL DEFAULT 1
        CHECK (quantity > 0),
    unit_price       REAL    NOT NULL DEFAULT 0.0
        CHECK (unit_price >= 0),
    discount         REAL    NOT NULL DEFAULT 0.0
        CHECK (discount >= 0 AND discount <= 1),
    discount_percent REAL    NOT NULL DEFAULT 0.0
        CHECK (discount_percent >= 0 AND discount_percent <= 1),
    line_total       REAL    NOT NULL DEFAULT 0.0
        CHECK (line_total >= 0),
    FOREIGN KEY (order_id) REFERENCES orders (order_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (product_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_orders_customer_id   ON orders (customer_id);
CREATE INDEX idx_orders_order_date    ON orders (order_date);
CREATE INDEX idx_orders_status        ON orders (status);
CREATE INDEX idx_products_category    ON products (category);
CREATE INDEX idx_order_items_order_id ON order_items (order_id);
CREATE INDEX idx_order_items_product  ON order_items (product_id);