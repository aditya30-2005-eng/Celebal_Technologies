

from scripts.utils import is_valid_email

def test_clean_customers_no_null_ids(cleaned_frames) -> None:
    customers = cleaned_frames["customers"]
    assert customers["customer_id"].notna().all()
    assert customers["customer_id"].is_unique

def test_clean_customers_all_emails_valid(cleaned_frames) -> None:
    customers = cleaned_frames["customers"]
    assert all(is_valid_email(value) for value in customers["email"])

def test_clean_products_no_duplicates(cleaned_frames) -> None:
    products = cleaned_frames["products"]
    assert products["product_id"].is_unique

def test_clean_products_positive_price(cleaned_frames) -> None:
    products = cleaned_frames["products"]
    assert (products["price"] > 0).all()

def test_clean_orders_valid_references(cleaned_frames) -> None:
    orders = cleaned_frames["orders"]
    customers = cleaned_frames["customers"]
    missing = ~orders["customer_id"].isin(set(customers["customer_id"]))
    assert not missing.any()
    assert orders["customer_id"].notna().all()

def test_clean_orders_no_future_dates(cleaned_frames) -> None:
    from datetime import date

    orders = cleaned_frames["orders"]
    assert all(orders["order_date"].dt.date <= date.today())

def test_clean_order_items_no_invalid_quantities(cleaned_frames) -> None:
    items = cleaned_frames["order_items"]
    assert (items["quantity"] > 0).all()

def test_clean_order_items_valid_discount(cleaned_frames) -> None:
    items = cleaned_frames["order_items"]
    assert ((items["discount"] >= 0) & (items["discount"] <= 1)).all()

def test_line_total_computed(cleaned_frames) -> None:
    items = cleaned_frames["order_items"]
    expected = (
        items["quantity"] * items["unit_price"] * (1 - items["discount"])
    ).round(2)
    assert (items["line_total"] - expected).abs().max() < 0.01

def test_cleaning_reports_written() -> None:
    from config import CLEANING_REPORT, EMAIL_REPORT

    assert CLEANING_REPORT.exists()
    assert EMAIL_REPORT.exists()
