
import io
import logging
import sqlite3
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    DB_PATH,
    OUTPUT_DIR,
    SQL_DIR,
    SCREENSHOT_DIR,
    ensure_directories,
)

logger = logging.getLogger(__name__)

def _render_text_to_png(text: str, path: Path, title: str) -> None:

    fig = plt.figure(figsize=(12, max(4, len(text.splitlines()) * 0.32)))
    fig.patch.set_facecolor("white")
    ax = fig.add_subplot(111)
    ax.text(
        0.01,
        0.99,
        text,
        family="DejaVu Sans Mono",
        fontsize=10,
        va="top",
        ha="left",
        transform=ax.transAxes,
    )
    ax.set_axis_off()
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    logger.info("Wrote screenshot %s", path)

def _run_cli(args: list[str]) -> str:

    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "report_cli.py"), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout + result.stderr

def _query_sql(sql_path: Path) -> str:

    query = sql_path.read_text(encoding="utf-8")
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute(query).fetchall()
        columns = [description[0] for description in connection.execute(
            query
        ).description]
    if not rows:
        return f"{sql_path.name}\nNo data."
    header = "  ".join(f"{col:<20}" for col in columns)
    lines = [header, "-" * len(header)]
    for row in rows[:20]:
        lines.append("  ".join(f"{str(value):<20}" for value in row))
    return "\n".join(lines)

def _pipeline_log_tail() -> str:

    log_path = PROJECT_ROOT / "logs" / "pipeline_screenshot.log"
    if not log_path.exists():
        return "Pipeline log not found. Run run_pipeline.py first."
    return log_path.read_text(encoding="utf-8")[-2000:]

def main() -> int:

    ensure_directories()

    pipeline_log = Path(PROJECT_ROOT / "logs" / "project.log")
    text = pipeline_log.read_text(encoding="utf-8")[-2000:]
    _render_text_to_png(
        text,
        SCREENSHOT_DIR / "01_pipeline.png",
        "Pipeline Execution (project.log)",
    )

    revenue = _query_sql(SQL_DIR / "basic" / "revenue_by_category.sql")
    _render_text_to_png(
        revenue,
        SCREENSHOT_DIR / "02_revenue_report.png",
        "SQL Report: Revenue by Category",
    )

    top_customers = _query_sql(SQL_DIR / "basic" / "top_customers.sql")
    _render_text_to_png(
        top_customers,
        SCREENSHOT_DIR / "03_top_customers.png",
        "SQL Report: Top 10 Customers",
    )

    cohort = _query_sql(SQL_DIR / "advanced" / "retention.sql")
    _render_text_to_png(
        cohort,
        SCREENSHOT_DIR / "04_cohort_retention.png",
        "SQL Report: Cohort / Retention",
    )

    cli_summary = _run_cli(
        ["--report", "weekly", "--start-date", "2026-01-01",
         "--end-date", "2026-01-07"]
    )
    _render_text_to_png(
        cli_summary,
        SCREENSHOT_DIR / "05_cli_summary.png",
        "CLI Report: Weekly Order Summary",
    )

    logger.info("All screenshots generated under %s", SCREENSHOT_DIR)
    return 0

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())