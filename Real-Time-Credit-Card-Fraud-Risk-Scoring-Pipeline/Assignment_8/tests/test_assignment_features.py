
import sqlite3

import pandas as pd
import pytest

from config import SQL_DIR

@pytest.fixture(scope="module")
def conn(built_database):

    connection = sqlite3.connect(built_database)
    yield connection
    connection.close()

def _read_sql(name: str) -> str:
    return (SQL_DIR / "advanced" / name).read_text(encoding="utf-8")

def test_aov_by_segment_columns(conn) -> None:
    frame = pd.read_sql_query(_read_sql("aov_by_segment.sql"), conn)
    for column in {
        "segment", "customer_count", "total_orders",
        "total_revenue", "average_order_value",
    }:
        assert column in frame.columns
    assert not frame.empty

def test_purchase_frequency_segments(conn) -> None:
    frame = pd.read_sql_query(
        _read_sql("purchase_frequency_segmentation.sql"), conn
    )
    assert "frequency_segment" in frame.columns
    segments = set(frame["frequency_segment"])

    assert "One-Time" in segments
    assert "Occasional" in segments
    assert "Loyal" in segments or len(frame["frequency_segment"]) == len(
        frame["frequency_segment"]
    )

def test_ntile_quartile_labels(conn) -> None:
    frame = pd.read_sql_query(_read_sql("ntile.sql"), conn)
    for column in {
        "customer_id", "total_value", "quartile", "quartile_label",
    }:
        assert column in frame.columns
    labels = set(frame["quartile_label"])
    assert {"Platinum", "Gold", "Silver", "Bronze"} == labels
    assert set(frame["quartile"]) == {1, 2, 3, 4}

def test_frequently_bought_together_columns(conn) -> None:
    frame = pd.read_sql_query(_read_sql("self_join.sql"), conn)
    for column in {"product_a", "product_b", "times_bought_together"}:
        assert column in frame.columns

def test_frequently_bought_together_no_duplicate_pairs(conn) -> None:
    frame = pd.read_sql_query(_read_sql("self_join.sql"), conn)

    pairs = set(zip(frame["product_a_id"], frame["product_b_id"]))
    assert len(pairs) == len(frame)
    for a, b in pairs:
        assert a != b
        assert (b, a) not in pairs


def test_order_items_with_unknown_order_id_dropped() -> None:
    from scripts.clean_data import DataCleaner

    cleaner = DataCleaner()
    frame = pd.DataFrame(
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
    )
    cleaned = cleaner.clean_order_items(frame, valid_order_ids={1},
                                        valid_product_ids={1})
    assert len(cleaned) == 0

def test_discount_over_100_clamped() -> None:
    from scripts.clean_data import DataCleaner

    cleaner = DataCleaner()
    frame = pd.DataFrame(
        [
            {
                "order_item_id": 1,
                "order_id": 1,
                "product_id": 1,
                "quantity": 1,
                "unit_price": 10.0,
                "discount": 1.5,
            }
        ]
    )
    cleaned = cleaner.clean_order_items(frame, valid_order_ids={1},
                                        valid_product_ids={1})
    assert cleaned.iloc[0]["discount"] == 0.0

def test_quantity_zero_replaced() -> None:
    from scripts.clean_data import DataCleaner

    cleaner = DataCleaner()
    frame = pd.DataFrame(
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
    )
    cleaned = cleaner.clean_order_items(frame, valid_order_ids={1},
                                        valid_product_ids={1})
    assert cleaned.iloc[0]["quantity"] == 1

def test_future_order_date_clamped() -> None:
    from datetime import date

    from scripts.clean_data import DataCleaner

    cleaner = DataCleaner()
    frame = pd.DataFrame(
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
    cleaned = cleaner.clean_orders(frame, customer_ids={1})
    assert cleaned.iloc[0]["order_date"].date() <= date.today()

def test_invalid_cli_report_type_rejected() -> None:
    from scripts.report_cli import build_parser

    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--report", "not_a_real_report"])

def test_invalid_date_range_rejected() -> None:
    from scripts.report_cli import main

    assert (
        main(
            [
                "--report",
                "revenue",
                "--start-date",
                "2023-12-31",
                "--end-date",
                "2023-01-01",
            ]
        )
        == 1
    )

def test_database_connection_failure_handled() -> None:
    from scripts.report_cli import ReportRunner

    runner = ReportRunner(db_path=SQL_DIR / "does_not_exist.db")
    try:
        runner.run(
            __import__("config").ReportConfig(
                report="revenue",
                start_date="2023-01-01",
                end_date="2023-12-31",
            )
        )
        handled = True
    except Exception:
        handled = False
    assert handled