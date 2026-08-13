

import pandas as pd

def test_generator_respects_custom_sizes(generator) -> None:

    customers = generator._customers_frame()
    products = generator._products_frame()
    orders = generator._orders_frame()
    order_items = generator._order_items_frame()

    assert len(customers) >= 60
    assert len(products) >= 40
    assert len(orders) >= 120
    assert len(order_items) >= 300

def test_generator_injects_invalid_emails(generator) -> None:

    customers = generator._customers_frame()
    invalid_share = customers["email"].apply(
        lambda value: "@" not in str(value)
    ).mean()
    assert invalid_share > 0

def test_generator_injects_future_dates(generator) -> None:

    from datetime import date, timedelta

    today = date.today()
    shifted = generator._maybe_future_date(1.0, today)
    assert shifted > today
    assert shifted <= today + timedelta(days=90)

def test_generator_injects_future_date_string_dd_mm_yyyy(generator) -> None:

    orders = generator._orders_frame()
    dd_mm = orders["order_date"].astype(str).str.match(r"^\d{2}-\d{2}-\d{4}$")
    assert dd_mm.any()

def test_generator_injects_negative_and_zero_quantities(generator) -> None:

    items = generator._order_items_frame()
    quantities = pd.to_numeric(items["quantity"], errors="coerce")
    assert (quantities <= 0).any()

def test_generator_injects_null_customer_ids(generator) -> None:

    generator_large = generator.__class__(
        seed=5, n_customers=20, n_products=20, n_orders=300, n_order_items=300,
    )
    orders = generator_large._orders_frame()
    null_customer = orders["customer_id"].isna() | (
        orders["customer_id"].astype(str).str.strip() == ""
    )
    assert null_customer.any()

def test_generator_injects_duplicates(generator) -> None:

    customers = generator._customers_frame()
    assert customers.duplicated(subset=["customer_id"]).any()

def test_generator_injects_leading_zero_product_ids(generator) -> None:

    products = generator._products_frame()
    padded = products["product_id"].astype(str).str.startswith("000")
    assert padded.any()
