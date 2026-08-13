
import logging
import sqlite3
import sys
from pathlib import Path

import pandas as pd

from config import DB_PATH, SQL_DIR, SAMPLE_OUTPUT_DIR, ensure_directories

logger = logging.getLogger(__name__)

SKIPPED_FILES = {"schema.sql", "views.sql"}

class SqlQueryRunner:

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found at {self.db_path}. "
                "Run `python run_pipeline.py` first."
            )
        return sqlite3.connect(self.db_path)

    def run_all(self) -> int:
        executed = 0
        failed = 0
        sql_files = sorted(SQL_DIR.rglob("*.sql"))
        with self._connect() as connection:
            for sql_file in sql_files:
                if sql_file.name in SKIPPED_FILES:
                    continue
                try:
                    query = sql_file.read_text(encoding="utf-8")
                    frame = pd.read_sql_query(query, connection)
                    relative = sql_file.relative_to(SQL_DIR)
                    out_path = SAMPLE_OUTPUT_DIR / f"{relative.stem}.csv"
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    frame.to_csv(out_path, index=False, encoding="utf-8")
                    executed += 1
                    logger.info(
                        "Executed %s (%s rows)", relative, len(frame)
                    )
                except sqlite3.Error as exc:
                    failed += 1
                    logger.error("Failed %s: %s", sql_file, exc)
        logger.info("Executed %s queries, %s failed", executed, failed)
        return failed

def main() -> None:

    logging.basicConfig(level=logging.INFO)
    ensure_directories()
    runner = SqlQueryRunner()
    failed = runner.run_all()
    if failed:
        raise SystemExit(f"{failed} query files failed to execute.")

if __name__ == "__main__":
    main()