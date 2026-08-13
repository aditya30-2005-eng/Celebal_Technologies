
import sqlite3
import time

from config import SQL_DIR, DB_PATH

def test_reference_database_exists() -> None:
    assert DB_PATH.exists()

def _time_query(query_path) -> tuple[float, int]:
    start = time.perf_counter()
    connection = sqlite3.connect(DB_PATH)
    try:
        rows = connection.execute(
            query_path.read_text(encoding="utf-8")
        ).fetchall()
    finally:
        connection.close()
    elapsed = time.perf_counter() - start
    return elapsed, len(rows)

def test_running_total_performance() -> None:
    elapsed, _ = _time_query(SQL_DIR / "advanced" / "running_total.sql")
    assert elapsed < 5.0

def test_window_functions_performance() -> None:
    elapsed, _ = _time_query(SQL_DIR / "advanced" / "window_functions.sql")
    assert elapsed < 5.0

def test_cohort_analysis_performance() -> None:
    elapsed, _ = _time_query(SQL_DIR / "advanced" / "cohort_analysis.sql")
    assert elapsed < 5.0

def test_rfm_performance() -> None:
    elapsed, _ = _time_query(SQL_DIR / "advanced" / "rfm.sql")
    assert elapsed < 5.0

def test_cumulative_distribution_performance() -> None:
    elapsed, _ = _time_query(
        SQL_DIR / "advanced" / "cumulative_distribution.sql"
    )
    assert elapsed < 5.0
