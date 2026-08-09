
import argparse
import logging
import re
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    DB_PATH,
    OUTPUT_CSV_DIR,
    OUTPUT_TXT_DIR,
    SQL_DIR,
    ReportConfig,
)
from scripts.utils import write_frame

logger = logging.getLogger(__name__)

REPORT_QUERIES: dict[str, str] = {
    "revenue": "basic/revenue_by_category.sql",
    "products": "basic/top_products.sql",
    "retention": "advanced/retention.sql",
    "cohort": "advanced/cohort_analysis.sql",
    "churn": "advanced/churn_detection.sql",
    "segmentation": "advanced/segmentation.sql",
    "rfm": "advanced/rfm.sql",
    "monthly_revenue": "basic/revenue_by_month.sql",
    "yearly": "advanced/year_over_year.sql",
}

REPORT_TITLES: dict[str, str] = {
    "revenue": "Revenue by Category",
    "products": "Top Products",
    "retention": "Customer Retention",
    "cohort": "Cohort Analysis",
    "churn": "Churn Detection",
    "segmentation": "Customer Segmentation",
    "rfm": "RFM Analysis",
    "monthly_revenue": "Monthly Revenue",
    "yearly": "Year-over-Year Revenue",
    "daily": "Daily Order Summary",
    "weekly": "Weekly Order Summary",
    "monthly": "Monthly Order Summary",
}


SUMMARY_REPORTS: set[str] = {"daily", "weekly", "monthly"}


MONTHLY_REVENUE_ALIAS = "monthly_revenue"


_REPORT_FILTERS: dict[str, set[str]] = {
    "revenue":    {"date", "category"},
    "products":   {"date", "category"},
    "retention":  set(),
    "cohort":     set(),
    "churn":      {"customer"},
    "segmentation": {"customer"},
    "rfm":        {"customer"},
    "monthly_revenue": {"date"},
    "yearly":     {"date"},
}

def _inject_where_clause(sql: str, condition: str) -> str:

    where_match = re.search(r"\bWHERE\b", sql, re.IGNORECASE)
    if not where_match:
        return sql
    after_where = sql[where_match.end():]
    end_match = re.search(r"\b(GROUP BY|ORDER BY|LIMIT|HAVING)\)?\s",
                          after_where, re.IGNORECASE)
    insert_pos = where_match.end() + end_match.start() if end_match else len(sql)
    return (
        sql[:where_match.end()]
        + f" {condition} AND"
        + sql[where_match.end():insert_pos]
        + sql[insert_pos:]
    )

class ReportRunner:

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found at {self.db_path}. "
                "Run `python run_pipeline.py` first."
            )
        connection = sqlite3.connect(self.db_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _load_query(report: str) -> str:

        if report in SUMMARY_REPORTS:
            raise ValueError(
                f"Report '{report}' is a summary report and has no SQL file."
            )
        relative = REPORT_QUERIES.get(report)
        if relative is None:
            raise ValueError(f"Unknown report: {report}")
        query_path = SQL_DIR / relative
        return query_path.read_text(encoding="utf-8")

    def _summary_previous_period(self, config: ReportConfig) -> tuple[str, str]:

        start = datetime.strptime(config.start_date, "%Y-%m-%d").date()
        end = datetime.strptime(config.end_date, "%Y-%m-%d").date()
        span = (end - start).days + 1
        prev_end = start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=span - 1)
        return prev_start.isoformat(), prev_end.isoformat()

    def fetch_summary(self, config: ReportConfig) -> dict[str, object]:

        if not config.start_date or not config.end_date:
            raise ValueError(
                "Summary reports require both --start-date and --end-date."
            )
        period_start = config.start_date
        period_end = config.end_date
        prev_start, prev_end = self._summary_previous_period(config)

        sql = """
        SELECT
            COUNT(DISTINCT o.order_id)                AS total_orders,
            ROUND(COALESCE(SUM(oi.line_total), 0), 2) AS total_revenue,
            COUNT(DISTINCT o.customer_id)             AS unique_customers
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
          AND o.order_date >= ? AND o.order_date <= ?
        """
        with self._connect() as connection:
            current = connection.execute(
                sql, (period_start, period_end)
            ).fetchone()
            previous = connection.execute(
                sql, (prev_start, prev_end)
            ).fetchone()
            top_products = connection.execute(
                """
                SELECT
                    p.product_name,
                    ROUND(SUM(oi.line_total), 2) AS revenue
                FROM products p
                JOIN order_items oi ON oi.product_id = p.product_id
                JOIN orders o       ON o.order_id = oi.order_id
                WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
                  AND o.order_date >= ? AND o.order_date <= ?
                GROUP BY p.product_id
                ORDER BY revenue DESC
                LIMIT 3
                """,
                (period_start, period_end),
            ).fetchall()

        total_orders = current[0] or 0
        total_revenue = current[1] or 0.0
        unique_customers = current[2] or 0
        prev_revenue = previous[1] or 0.0

        if prev_revenue:
            change_pct = round(
                100.0 * (total_revenue - prev_revenue) / prev_revenue, 2
            )
        else:
            change_pct = None

        return {
            "period_type": config.report,
            "start_date": period_start,
            "end_date": period_end,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "unique_customers": unique_customers,
            "top_products": [(row[0], row[1]) for row in top_products],
            "previous_start": prev_start,
            "previous_end": prev_end,
            "previous_revenue": prev_revenue,
            "revenue_change": round(total_revenue - prev_revenue, 2),
            "change_pct": change_pct,
        }

    def render_summary(self, summary: dict[str, object]) -> str:

        lines = [
            "=" * 40,
            "E-COMMERCE ORDER SUMMARY",
            "=" * 40,
            "",
            f"Period: {summary['period_type'].capitalize()}",
            f"Start Date: {summary['start_date']}",
            f"End Date:   {summary['end_date']}",
            "",
            f"Total Orders:      {summary['total_orders']}",
            f"Total Revenue:     {summary['total_revenue']}",
            f"Unique Customers:  {summary['unique_customers']}",
            "",
            "Top 3 Products:",
        ]
        if summary["top_products"]:
            for index, (name, revenue) in enumerate(
                summary["top_products"], start=1
            ):
                lines.append(f"{index}. {name} ({revenue})")
        else:
            lines.append("No products sold in this period.")
        lines.extend(
            [
                "",
                "Previous Period:",
                f"Previous Revenue: {summary['previous_revenue']}",
                f"Revenue Change:   {summary['revenue_change']}",
                "Percentage Change:",
            ]
        )
        if summary["change_pct"] is None:
            lines.append("N/A (no previous-period revenue)")
        else:
            lines.append(f"{summary['change_pct']}%")
        lines.extend(["", "=" * 40])
        return "\n".join(lines)

    def _summary_block(self, config: ReportConfig) -> str:

        summary = self.fetch_summary(config)
        return self.render_summary(summary)

    def fetch(self, config: ReportConfig) -> pd.DataFrame:

        if config.report in SUMMARY_REPORTS:
            raise ValueError(
                f"Report '{config.report}' is a summary report; "
                "use the summary methods instead."
            )
        query = self._load_query(config.report)
        supported = _REPORT_FILTERS.get(config.report, set())
        params: list[object] = []

        if config.start_date:
            if "date" not in supported:
                raise ValueError(
                    f"Report '{config.report}' does not support date filtering."
                )
            query = _inject_where_clause(
                query, "o.order_date >= ?"
            )
            params.append(config.start_date)
        if config.end_date:
            if "date" not in supported:
                raise ValueError(
                    f"Report '{config.report}' does not support date filtering."
                )
            query = _inject_where_clause(
                query, "o.order_date <= ?"
            )
            params.append(config.end_date)
        if config.category:
            if "category" not in supported:
                raise ValueError(
                    f"Report '{config.report}' does not support category filtering."
                )
            query = _inject_where_clause(
                query, "p.category = ?"
            )
            params.append(config.category)
        if config.customer_id:
            if "customer" not in supported:
                raise ValueError(
                    f"Report '{config.report}' does not support customer-id filtering."
                )
            query = _inject_where_clause(
                query, "o.customer_id = ?"
            )
            params.append(int(config.customer_id))
        with self._connect() as connection:
            return pd.read_sql_query(query, connection, params=params)

    def render(self, frame: pd.DataFrame, title: str) -> str:

        if frame.empty:
            return f"{title}\n{'=' * 40}\nNo data available for this report."
        header = f"{title}\n{'=' * 120}"
        return f"{header}\n{frame.to_string(index=False, max_colwidth=28)}"

    def export(self, frame: pd.DataFrame, config: ReportConfig) -> None:

        if not config.export_format:
            return
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{config.report}_{stamp}"
        if config.export_format == "csv":
            path = OUTPUT_CSV_DIR / f"{base_name}.csv"
            write_frame(frame, path)
        elif config.export_format == "txt":
            path = OUTPUT_TXT_DIR / f"{base_name}.txt"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                self.render(frame, REPORT_TITLES[config.report]),
                encoding="utf-8",
            )
        else:
            raise ValueError(
                f"Unsupported export format: {config.export_format}"
            )
        logger.info("Exported report to %s", path)

    def run(self, config: ReportConfig) -> int:

        try:
            if config.report in SUMMARY_REPORTS:
                rendered = self._summary_block(config)
            else:
                frame = self.fetch(config)
                rendered = self.render(frame, REPORT_TITLES[config.report])
            sys.stdout.write(rendered + "\n")
            sys.stdout.flush()
            return 0
        except (FileNotFoundError, ValueError, sqlite3.Error) as exc:
            sys.stderr.write(f"Error: {exc}\n")
            return 1

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog="report_cli.py",
        description="E-Commerce Order Analytics System - report runner.",
    )
    parser.add_argument(
        "--report",
        required=True,
        choices=sorted(set(REPORT_QUERIES.keys()) | SUMMARY_REPORTS),
        help="The report to run: analytical report or daily/weekly/monthly summary.",
    )
    parser.add_argument(
        "--customer-id",
        type=int,
        default=None,
        help="Filter results to a specific customer id.",
    )
    parser.add_argument(
        "--category",
        default=None,
        help="Filter results to a product category.",
    )
    parser.add_argument(
        "--start-date",
        default=None,
        help="Include orders on or after this date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--end-date",
        default=None,
        help="Include orders on or before this date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--export",
        choices=["csv", "txt"],
        default=None,
        help="Export the report to a file.",
    )
    return parser

def validate_date(value: str | None) -> None:

    if value is None:
        return
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(
            f"Invalid date '{value}'. Expected format YYYY-MM-DD."
        ) from exc

def _configure_stdout() -> None:

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass

def main(argv: list[str] | None = None) -> int:

    _configure_stdout()
    logging.basicConfig(level=logging.INFO)
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        validate_date(args.start_date)
        validate_date(args.end_date)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.start_date and args.end_date and args.start_date > args.end_date:
        print("Error: --start-date must not be after --end-date.",
              file=sys.stderr)
        return 1

    config = ReportConfig(
        report=args.report,
        customer_id=args.customer_id,
        category=args.category,
        start_date=args.start_date,
        end_date=args.end_date,
        export_format=args.export,
    )
    return ReportRunner().run(config)

if __name__ == "__main__":
    raise SystemExit(main())