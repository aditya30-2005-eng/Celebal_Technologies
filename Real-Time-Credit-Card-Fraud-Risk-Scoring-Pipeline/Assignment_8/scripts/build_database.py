
import logging
import sqlite3
from pathlib import Path

import pandas as pd

from config import (
    CLEAN_CUSTOMERS,
    CLEAN_PRODUCTS,
    CLEAN_ORDERS,
    CLEAN_ORDER_ITEMS,
    DB_PATH,
    SQL_DIR,
)
from scripts.utils import read_frame

logger = logging.getLogger(__name__)

SCHEMA_FILE = SQL_DIR / "schema.sql"
VIEWS_FILE = SQL_DIR / "views.sql"

TABLE_EXPECTATIONS: dict[str, int] = {
    "customers": 0,
    "products": 0,
    "orders": 0,
    "order_items": 0,
}

class DatabaseBuilder:

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_path)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def create_schema(self) -> None:
        with self._connect() as connection:
            connection.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
        logger.info("Executed %s", SCHEMA_FILE)

    def create_views(self) -> None:
        with self._connect() as connection:
            connection.executescript(VIEWS_FILE.read_text(encoding="utf-8"))
        logger.info("Executed %s", VIEWS_FILE)

    def _insert_frame(self, connection: sqlite3.Connection,
                      table: str, frame: pd.DataFrame) -> None:
        frame.to_sql(
            table,
            connection,
            if_exists="append",
            index=False,
        )

    def populate(self, clean_paths: dict[str, Path] | None = None) -> None:
        paths = clean_paths or {
            "customers": CLEAN_CUSTOMERS,
            "products": CLEAN_PRODUCTS,
            "orders": CLEAN_ORDERS,
            "order_items": CLEAN_ORDER_ITEMS,
        }
        customers = read_frame(paths["customers"])
        products = read_frame(paths["products"])
        orders = read_frame(paths["orders"])
        order_items = read_frame(paths["order_items"])

        TABLE_EXPECTATIONS["customers"] = len(customers)
        TABLE_EXPECTATIONS["products"] = len(products)
        TABLE_EXPECTATIONS["orders"] = len(orders)
        TABLE_EXPECTATIONS["order_items"] = len(order_items)

        with self._connect() as connection:
            self._insert_frame(connection, "customers", customers)
            self._insert_frame(connection, "products", products)
            self._insert_frame(connection, "orders", orders)
            self._insert_frame(connection, "order_items", order_items)

        logger.info(
            "Loaded customers=%s products=%s orders=%s order_items=%s",
            len(customers),
            len(products),
            len(orders),
            len(order_items),
        )

    def verify(self) -> bool:
        with self._connect() as connection:
            for table, expected in TABLE_EXPECTATIONS.items():
                actual = connection.execute(
                    f"SELECT COUNT(*) FROM {table}"
                ).fetchone()[0]
                status = "OK" if actual == expected else "MISMATCH"
                logger.info(
                    "Verification %s: %s expected=%s actual=%s",
                    status,
                    table,
                    expected,
                    actual,
                )
                if actual != expected:
                    return False
        return True

    def build(
        self,
        clean_paths: dict[str, Path] | None = None,
    ) -> bool:

        self.create_schema()
        self.populate(clean_paths)
        self.create_views()
        return self.verify()

def main() -> None:

    logging.basicConfig(level=logging.INFO)
    builder = DatabaseBuilder()
    success = builder.build()
    if not success:
        raise SystemExit("Database verification failed.")

if __name__ == "__main__":
    main()