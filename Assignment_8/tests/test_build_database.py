

import sqlite3

from config import SQL_DIR

def test_tables_created(built_database) -> None:
    connection = sqlite3.connect(built_database)
    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    connection.close()
    for expected in {"customers", "products", "orders", "order_items"}:
        assert expected in tables

def test_views_created(built_database) -> None:
    connection = sqlite3.connect(built_database)
    views = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='view'"
        )
    }
    connection.close()
    for expected in {
        "customer_summary",
        "product_summary",
        "monthly_revenue",
        "top_products",
    }:
        assert expected in views

def test_foreign_keys_enforced(built_database) -> None:
    connection = sqlite3.connect(built_database)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        connection.execute(
            "INSERT INTO orders (order_id, customer_id, order_date, status,"
            " payment_method, shipping_region)"
            " VALUES (999999, -1, '2023-01-01', 'PENDING', 'cash','North')"
        )
        raised = False
    except sqlite3.IntegrityError:
        raised = True
    connection.close()
    assert raised

def test_no_orphan_rows(built_database) -> None:
    connection = sqlite3.connect(built_database)
    orphans = connection.execute(
        "SELECT COUNT(*) FROM orders o"
        " LEFT JOIN customers c ON c.customer_id = o.customer_id"
        " WHERE c.customer_id IS NULL"
    ).fetchone()[0]
    connection.close()
    assert orphans == 0

def test_duplicate_primary_key_rejected(built_database) -> None:
    connection = sqlite3.connect(built_database)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            "INSERT INTO customers (customer_id, name, email, region,"
            " city, joined_date) VALUES (1, 'Dup', 'dup@example.com',"
            " 'North','City','2023-01-01')"
        )
        raised = False
    except sqlite3.IntegrityError:
        raised = True
    finally:
        connection.close()
    assert raised

def test_not_null_constraint_blocks_nulls(built_database) -> None:
    connection = sqlite3.connect(built_database)
    try:
        connection.execute(
            "INSERT INTO products (product_id, product_name) VALUES (99999, NULL)"
        )
        raised = False
    except sqlite3.IntegrityError:
        raised = True
    finally:
        connection.close()
    assert raised

def test_schema_file_exists() -> None:
    assert (SQL_DIR / "schema.sql").exists()
    assert (SQL_DIR / "views.sql").exists()

def test_query_files_present() -> None:
    basic = SQL_DIR / "basic"
    intermediate = SQL_DIR / "intermediate"
    advanced = SQL_DIR / "advanced"
    assert len(list(basic.glob("*.sql"))) >= 5
    assert len(list(intermediate.glob("*.sql"))) >= 3
    assert len(list(advanced.glob("*.sql"))) >= 20
