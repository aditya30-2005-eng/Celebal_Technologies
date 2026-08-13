

from datetime import date

import pandas as pd

from scripts.clean_data import DataCleaner

def _frame(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)

def test_future_dates_clamped_to_today() -> None:
    cleaner = DataCleaner()
    orders = _frame(
        [
            {
                "order_id": 1,
                "customer_id": 1,
                "order_date": "2099-12-31",
                "status": "PENDING",
                "payment_method": "cash",
                "shipping_region": "North",
            }
        ]
    )
    cleaned = cleaner.clean_orders(orders, {1})
    assert cleaned.iloc[0]["order_date"].date() <= date.today()

def test_discount_over_100_clamped() -> None:
    cleaner = DataCleaner()
    cleaned = cleaner.clean_order_items(
        _frame(
            [
                {
                    "order_item_id": 1,
                    "order_id": 1,
                    "product_id": 1,
                    "quantity": 2,
                    "unit_price": 10.0,
                    "discount": 1.5,
                }
            ]
        ),
        {1},
        {1},
    )
    assert cleaned.iloc[0]["discount"] == 0.0

def test_quantity_zero_replaced() -> None:
    cleaner = DataCleaner()
    cleaned = cleaner.clean_order_items(
        _frame(
            [
                {
                    "order_item_id": 1,
                    "order_id": 1,
                    "product_id": 1,
                    "quantity": 0,
                    "unit_price": 10.0,
                    "discount": 0.0,
                }
            ]
        ),
        {1},
        {1},
    )
    assert cleaned.iloc[0]["quantity"] == 1

def test_negative_quantity_abs() -> None:
    cleaner = DataCleaner()
    cleaned = cleaner.clean_order_items(
        _frame(
            [
                {
                    "order_item_id": 1,
                    "order_id": 1,
                    "product_id": 1,
                    "quantity": -4,
                    "unit_price": 10.0,
                    "discount": 0.0,
                }
            ]
        ),
        {1},
        {1},
    )
    assert cleaned.iloc[0]["quantity"] == 4

def test_negative_discount_clamped() -> None:
    cleaner = DataCleaner()
    cleaned = cleaner.clean_order_items(
        _frame(
            [
                {
                    "order_item_id": 1,
                    "order_id": 1,
                    "product_id": 1,
                    "quantity": 1,
                    "unit_price": 10.0,
                    "discount": -0.2,
                }
            ]
        ),
        {1},
        {1},
    )
    assert cleaned.iloc[0]["discount"] == 0.0

def test_invalid_order_id_dropped() -> None:
    cleaner = DataCleaner()
    cleaned = cleaner.clean_order_items(
        _frame(
            [
                {
                    "order_item_id": 1,
                    "order_id": 999,
                    "product_id": 1,
                    "quantity": 1,
                    "unit_price": 10.0,
                    "discount": 0.0,
                }
            ]
        ),
        {1},
        {1},
    )
    assert len(cleaned) == 0

def test_duplicate_products_deduplicated() -> None:
    cleaner = DataCleaner()
    products = _frame(
        [
            {"product_id": 1, "product_name": "A", "category": "Cat",
             "brand": "B", "price": 10.0, "stock_quantity": 5},
            {"product_id": 1, "product_name": "A", "category": "Cat",
             "brand": "B", "price": 10.0, "stock_quantity": 5},
        ]
    )
    cleaned = cleaner.clean_products(products)
    assert len(cleaned) == 1

def test_missing_customer_dropped() -> None:
    cleaner = DataCleaner()
    orders = _frame(
        [
            {
                "order_id": 1,
                "customer_id": None,
                "order_date": "2023-01-01",
                "status": "PENDING",
                "payment_method": "cash",
                "shipping_region": "North",
            }
        ]
    )
    cleaned = cleaner.clean_orders(orders, {1, 2})
    assert len(cleaned) == 0

def test_empty_dataset_returns_empty() -> None:
    cleaner = DataCleaner()
    cleaned = cleaner.clean_products(pd.DataFrame(columns=["product_id"]))
    assert len(cleaned) == 0

def test_single_customer_processes() -> None:
    cleaner = DataCleaner()
    orders = _frame(
        [
            {
                "order_id": 1,
                "customer_id": 1,
                "order_date": "2023-01-01",
                "status": "DELIVERED",
                "payment_method": "cash",
                "shipping_region": "North",
            }
        ]
    )
    cleaned = cleaner.clean_orders(orders, {1})
    assert len(cleaned) == 1

def test_wrong_datatype_id_coerced() -> None:
    cleaner = DataCleaner()
    customers = _frame(
        [
            {
                "customer_id": "007",
                "name": "Alice",
                "email": "alice@example.com",
                "region": "North",
                "city": "City",
                "joined_date": "2023-01-01",
            }
        ]
    )
    cleaned = cleaner.clean_customers(customers)
    assert cleaned.iloc[0]["customer_id"] == 7

def test_missing_price_filled() -> None:
    cleaner = DataCleaner()
    products = _frame(
        [
            {"product_id": 1, "product_name": "A", "category": "Cat",
             "brand": "B", "price": None, "stock_quantity": 5}
        ]
    )
    cleaned = cleaner.clean_products(products)
    assert cleaned.iloc[0]["price"] > 0

def test_invalid_email_removed() -> None:
    cleaner = DataCleaner()
    customers = _frame(
        [
            {
                "customer_id": 1,
                "name": "Alice",
                "email": "not-an-email",
                "region": "North",
                "city": "City",
                "joined_date": "2023-01-01",
            }
        ]
    )
    cleaned = cleaner.clean_customers(customers)
    assert len(cleaned) == 0
