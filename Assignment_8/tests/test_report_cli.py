

from pathlib import Path

import pandas as pd
import pytest

from config import OUTPUT_CSV_DIR, OUTPUT_TXT_DIR, ReportConfig
from scripts.report_cli import (
    ReportRunner,
    build_parser,
    validate_date,
)

def test_build_parser_requires_report() -> None:
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])

def test_validate_date_accepts_valid() -> None:
    validate_date("2023-01-15")

def test_validate_date_rejects_invalid() -> None:
    try:
        validate_date("not-a-date")
        raised = False
    except ValueError:
        raised = True
    assert raised

def test_validate_date_rejects_impossible_calendar() -> None:
    try:
        validate_date("2023-13-45")
        raised = False
    except ValueError:
        raised = True
    assert raised

def test_report_runner_revenue(built_database) -> None:
    runner = ReportRunner(db_path=built_database)
    frame = runner.fetch(ReportConfig(report="revenue"))
    assert not frame.empty
    assert "category" in frame.columns
    assert "revenue" in frame.columns

def test_report_runner_products(built_database) -> None:
    runner = ReportRunner(db_path=built_database)
    frame = runner.fetch(ReportConfig(report="products"))
    assert not frame.empty
    assert "revenue_rank" in frame.columns

def test_report_runner_monthly_revenue(built_database) -> None:
    runner = ReportRunner(db_path=built_database)
    frame = runner.fetch(ReportConfig(report="monthly_revenue"))
    assert not frame.empty
    assert "month_key" in frame.columns

def test_report_runner_yearly(built_database) -> None:
    runner = ReportRunner(db_path=built_database)
    frame = runner.fetch(ReportConfig(report="yearly"))
    assert not frame.empty
    assert "change_pct" in frame.columns

def test_report_runner_rfm_columns(built_database) -> None:
    runner = ReportRunner(db_path=built_database)
    frame = runner.fetch(ReportConfig(report="rfm"))
    for column in {"r_score", "f_score", "m_score", "rfm_cell"}:
        assert column in frame.columns

def test_report_runner_revenue_date_filter(built_database) -> None:
    runner = ReportRunner(db_path=built_database)
    frame = runner.fetch(
        ReportConfig(report="revenue", start_date="2023-01-01")
    )
    assert not frame.empty

def test_report_runner_revenue_category_filter(built_database) -> None:
    runner = ReportRunner(db_path=built_database)
    frame = runner.fetch(
        ReportConfig(report="revenue", category="Electronics")
    )
    assert set(frame["category"]) == {"Electronics"}

def test_report_runner_unsupported_category_raises(built_database) -> None:
    runner = ReportRunner(db_path=built_database)
    try:
        runner.fetch(ReportConfig(report="rfm", category="Electronics"))
        raised = False
    except ValueError:
        raised = True
    assert raised

def test_report_runner_customer_id_filter(built_database) -> None:
    runner = ReportRunner(db_path=built_database)
    frame = runner.fetch(ReportConfig(report="rfm", customer_id=1))
    assert not frame.empty
    assert set(frame["customer_id"]) == {1}

def test_report_runner_unsupported_customer_raises(built_database) -> None:
    runner = ReportRunner(db_path=built_database)
    try:
        runner.fetch(ReportConfig(report="revenue", customer_id=1))
        raised = False
    except ValueError:
        raised = True
    assert raised

def test_missing_database_raises(work_dir) -> None:
    missing = work_dir / "does_not_exist.db"
    runner = ReportRunner(db_path=missing)
    try:
        runner.fetch(ReportConfig(report="revenue"))
        raised = False
    except FileNotFoundError:
        raised = True
    assert raised

def test_render_empty_frame() -> None:
    runner = ReportRunner()
    output = runner.render(pd.DataFrame(), "Empty Report")
    assert "No data available" in output

def test_export_writes_files(built_database) -> None:
    runner = ReportRunner(db_path=built_database)
    frame = runner.fetch(ReportConfig(report="monthly_revenue"))

    for export_format, export_dir in (("csv", OUTPUT_CSV_DIR),
                                      ("txt", OUTPUT_TXT_DIR)):
        runner.export(
            frame,
            ReportConfig(
                report="monthly_revenue", export_format=export_format
            ),
        )
        written = (
            list(Path(export_dir).glob("monthly_revenue_*.csv"))
            if export_format == "csv"
            else list(Path(export_dir).glob("monthly_revenue_*.txt"))
        )
        assert written
        content = (
            pd.read_csv(written[-1])
            if export_format == "csv"
            else written[-1].read_text(encoding="utf-8")
        )
        assert len(content) > 0


def test_fetch_summary_requires_dates(built_database) -> None:
    runner = ReportRunner(db_path=built_database)
    try:
        runner.fetch_summary(ReportConfig(report="daily"))
        raised = False
    except ValueError:
        raised = True
    assert raised

def test_fetch_summary_daily(built_database) -> None:
    runner = ReportRunner(db_path=built_database)
    summary = runner.fetch_summary(
        ReportConfig(
            report="daily",
            start_date="2023-01-01",
            end_date="2023-01-01",
        )
    )
    assert summary["total_orders"] >= 0
    assert summary["total_revenue"] >= 0
    assert summary["unique_customers"] >= 0
    assert "top_products" in summary
    assert "previous_revenue" in summary
    assert "change_pct" in summary

def test_fetch_summary_weekly(built_database) -> None:
    runner = ReportRunner(db_path=built_database)
    summary = runner.fetch_summary(
        ReportConfig(
            report="weekly",
            start_date="2023-01-01",
            end_date="2023-01-07",
        )
    )
    assert summary["period_type"] == "weekly"
    assert summary["total_orders"] >= 0

def test_fetch_summary_monthly(built_database) -> None:
    runner = ReportRunner(db_path=built_database)
    summary = runner.fetch_summary(
        ReportConfig(
            report="monthly",
            start_date="2023-01-01",
            end_date="2023-01-31",
        )
    )
    assert summary["period_type"] == "monthly"
    assert summary["total_revenue"] >= 0

def test_render_summary_contains_required_fields() -> None:
    runner = ReportRunner()
    summary = {
        "period_type": "daily",
        "start_date": "2023-01-01",
        "end_date": "2023-01-01",
        "total_orders": 5,
        "total_revenue": 100.0,
        "unique_customers": 3,
        "top_products": [("A", 50.0), ("B", 30.0), ("C", 20.0)],
        "previous_revenue": 80.0,
        "revenue_change": 20.0,
        "change_pct": 25.0,
    }
    output = runner.render_summary(summary)
    for token in (
        "E-COMMERCE ORDER SUMMARY",
        "Total Orders:",
        "Total Revenue:",
        "Unique Customers:",
        "Top 3 Products:",
        "Previous Revenue:",
        "Revenue Change:",
        "Percentage Change:",
    ):
        assert token in output

def test_summary_empty_result_handled(built_database) -> None:

    runner = ReportRunner(db_path=built_database)
    summary = runner.fetch_summary(
        ReportConfig(
            report="daily",
            start_date="2099-01-01",
            end_date="2099-01-01",
        )
    )
    assert summary["total_orders"] == 0
    assert summary["total_revenue"] == 0
    assert summary["top_products"] == []
    rendered = runner.render_summary(summary)
    assert "No products sold in this period." in rendered

def test_summary_previous_period_calculation() -> None:
    runner = ReportRunner()
    prev_start, prev_end = runner._summary_previous_period(
        ReportConfig(
            report="daily",
            start_date="2023-01-10",
            end_date="2023-01-10",
        )
    )
    assert prev_end == "2023-01-09"
    assert prev_start == "2023-01-09"

def test_summary_missing_database_raises(work_dir) -> None:
    missing = work_dir / "nope.db"
    runner = ReportRunner(db_path=missing)
    try:
        runner.fetch_summary(
            ReportConfig(
                report="monthly",
                start_date="2023-01-01",
                end_date="2023-01-31",
            )
        )
        raised = False
    except FileNotFoundError:
        raised = True
    assert raised