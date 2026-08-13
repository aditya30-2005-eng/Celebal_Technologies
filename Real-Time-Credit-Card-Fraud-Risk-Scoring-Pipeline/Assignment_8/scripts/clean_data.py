
import logging
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from config import (
    CLEAN_CUSTOMERS,
    CLEAN_PRODUCTS,
    CLEAN_ORDERS,
    CLEAN_ORDER_ITEMS,
    CLEANING_REPORT,
    VALIDATION_REPORT,
    EMAIL_REPORT,
    REFERENTIAL_INTEGRITY_REPORT,
    RAW_CUSTOMERS,
    RAW_PRODUCTS,
    RAW_ORDERS,
    RAW_ORDER_ITEMS,
)
from scripts.utils import (
    is_valid_email,
    normalize_text,
    read_frame,
    to_float,
    to_int,
    write_frame,
)

logger = logging.getLogger(__name__)

class IssueTracker:

    def __init__(self) -> None:
        self.issues: list[tuple[str, int, str, str]] = []

    def record(self, entity: str, row_id: int | None,
               field: str, message: str) -> None:
        self.issues.append((entity, row_id, field, message))

    def count(self) -> int:
        return len(self.issues)

    def summary_counts(self) -> Counter:
        return Counter(issue[0] for issue in self.issues)

    def write_report(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "E-Commerce Order Analytics System - Cleaning Report",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total issues found: {self.count()}",
            "",
            "Summary by entity:",
        ]
        for entity, count in self.summary_counts().most_common():
            lines.append(f"  {entity:<14} {count}")
        lines.append("")
        lines.append(f"{'Entity':<14} {'Row ID':<8} {'Field':<18} Issue")
        lines.append("-" * 60)
        for entity, row_id, field, message in self.issues:
            lines.append(
                f"{entity:<14} {str(row_id):<8} {field:<18} {message}"
            )
        path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Wrote cleaning report to %s", path)

class DataCleaner:

    def __init__(self) -> None:
        self.tracker = IssueTracker()


    def clean_customers(self, frame: pd.DataFrame) -> pd.DataFrame:
        original = len(frame)
        frame = frame.copy()
        frame["customer_id"] = frame["customer_id"].map(
            lambda value: to_int(value, default=None)
        )
        frame = frame.dropna(subset=["customer_id"])
        for row_id, value in zip(frame["customer_id"], frame["email"]):
            if not is_valid_email(value):
                self.tracker.record("customers", row_id, "email",
                                    "invalid email format")
        frame = frame.drop_duplicates(subset=["customer_id"], keep="first")
        frame["name"] = frame["name"].map(normalize_text).str.title()
        frame["email"] = frame["email"].map(
            lambda value: str(value).strip().lower() if value else ""
        )
        frame = frame.drop_duplicates(subset=["email"], keep="first")
        frame["name"] = frame["name"].replace("", "Unknown Customer")
        valid_types = {
            "REGULAR", "PREMIUM", "VIP", "NEW",
        }
        if "customer_type" in frame.columns:
            frame["customer_type"] = (
                frame["customer_type"]
                .map(normalize_text)
                .str.upper()
                .replace("", "REGULAR")
            )
            frame["customer_type"] = frame["customer_type"].where(
                frame["customer_type"].isin(valid_types), "REGULAR"
            )
        else:
            frame["customer_type"] = "REGULAR"
        frame["region"] = frame["region"].map(normalize_text).str.title()
        frame["region"] = frame["region"].replace("", "Unknown")
        frame["city"] = frame["city"].map(normalize_text).str.title()
        frame["city"] = frame["city"].replace("", "Unknown")
        frame["joined_date"] = pd.to_datetime(
            frame["joined_date"], errors="coerce", format="mixed"
        ).dt.date
        frame["joined_date"] = frame["joined_date"].fillna(
            date(2020, 1, 1)
        )
        frame = frame[frame["joined_date"] <= date.today()]
        frame = frame[frame["email"].apply(is_valid_email)]
        frame = frame.sort_values("customer_id").reset_index(drop=True)

        frame["customer_name"] = frame["name"]
        frame["registration_date"] = frame["joined_date"]
        logger.info(
            "customers: %s -> %s (dropped %s)",
            original, len(frame), original - len(frame),
        )
        return frame


    def clean_products(self, frame: pd.DataFrame) -> pd.DataFrame:
        original = len(frame)
        if frame.empty or "product_id" not in frame.columns:
            logger.info("products: empty input, returning empty frame")
            return pd.DataFrame(
                columns=[
                    "product_id", "product_name", "category", "subcategory",
                    "brand", "price", "cost_price", "stock_quantity",
                ]
            )
        frame = frame.copy()
        frame["product_id"] = frame["product_id"].map(
            lambda value: to_int(value, default=None)
        )
        frame = frame.dropna(subset=["product_id"])
        frame = frame.drop_duplicates(subset=["product_id"], keep="first")
        frame["product_name"] = frame["product_name"].map(normalize_text)
        frame["product_name"] = frame["product_name"].str.title()
        frame["product_name"] = frame["product_name"].replace(
            "", "Unnamed Product"
        )
        frame["category"] = frame["category"].map(normalize_text).str.title()
        frame["category"] = frame["category"].replace("", "Uncategorized")
        if "subcategory" in frame.columns:
            frame["subcategory"] = (
                frame["subcategory"].map(normalize_text).str.title()
            )
            frame["subcategory"] = frame["subcategory"].replace(
                "", "General"
            )
        else:
            frame["subcategory"] = "General"
        frame["brand"] = frame["brand"].map(normalize_text).str.title()
        frame["brand"] = frame["brand"].replace("", "Unknown")
        frame["price"] = frame["price"].map(lambda value: to_float(value))
        frame["price"] = frame["price"].where(frame["price"] > 0, 19.99)
        if "cost_price" in frame.columns:
            cost = frame["cost_price"].map(lambda value: to_float(value))
            frame["cost_price"] = cost.where(
                (cost > 0) & (cost <= frame["price"]), frame["price"]
            )
        else:
            frame["cost_price"] = frame["price"]
        frame["stock_quantity"] = frame["stock_quantity"].map(
            lambda value: max(to_int(value), 0)
        )
        frame = frame.sort_values("product_id").reset_index(drop=True)
        logger.info(
            "products: %s -> %s (dropped %s)",
            original, len(frame), original - len(frame),
        )
        return frame


    def clean_orders(self, frame: pd.DataFrame,
                     customer_ids: set[int]) -> pd.DataFrame:
        original = len(frame)
        frame = frame.copy()
        frame["order_id"] = frame["order_id"].map(
            lambda value: to_int(value, default=None)
        )
        frame = frame.dropna(subset=["order_id"])
        frame = frame.drop_duplicates(subset=["order_id"], keep="first")
        frame["customer_id"] = frame["customer_id"].map(
            lambda value: to_int(value, default=None)
        )
        missing = frame["customer_id"].isna().sum()
        self.tracker.record("orders", None, "customer_id",
                            f"{missing} rows missing customer_id")
        frame = frame.dropna(subset=["customer_id"])
        invalid_fk = ~frame["customer_id"].isin(customer_ids)
        for row_id in frame.loc[invalid_fk, "order_id"]:
            self.tracker.record("orders", row_id, "customer_id",
                                "customer_id has no matching customer")
        frame = frame[~invalid_fk]
        frame["order_date"] = frame["order_date"].map(
            lambda value: self._parse_date(value)
        )
        future = frame["order_date"] > date.today()
        for row_id in frame.loc[future, "order_id"]:
            self.tracker.record("orders", row_id, "order_date",
                                "order_date is in the future")
        frame["order_date"] = frame["order_date"].where(~future, date.today())
        frame["order_date"] = pd.to_datetime(frame["order_date"])
        frame["status"] = frame["status"].map(normalize_text).str.upper()
        valid_statuses = {
            "PENDING", "PROCESSING", "SHIPPED", "DELIVERED",
            "CANCELLED", "RETURNED", "REFUNDED",
        }
        frame["status"] = frame["status"].where(
            frame["status"].isin(valid_statuses), "PENDING"
        )
        frame["payment_method"] = frame["payment_method"].map(
            normalize_text
        ).str.lower()
        frame["payment_method"] = frame["payment_method"].replace("", "unknown")
        frame["shipping_region"] = frame["shipping_region"].map(
            normalize_text
        ).str.title()
        frame["shipping_region"] = frame["shipping_region"].replace(
            "", "Unknown"
        )
        frame = frame.sort_values("order_id").reset_index(drop=True)

        frame["region_code"] = frame["shipping_region"]
        logger.info(
            "orders: %s -> %s (dropped %s)",
            original, len(frame), original - len(frame),
        )
        return frame

    @staticmethod
    def _parse_date(value) -> date:
        if value is None or value == "":
            return date.today()
        if isinstance(value, date):
            return value
        text = str(value).strip()
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        return date.today()


    def clean_order_items(
        self,
        frame: pd.DataFrame,
        valid_order_ids: set[int],
        valid_product_ids: set[int],
    ) -> pd.DataFrame:
        original = len(frame)
        frame = frame.copy()
        frame["order_item_id"] = frame["order_item_id"].map(
            lambda value: to_int(value, default=None)
        )
        frame = frame.dropna(subset=["order_item_id"])
        frame = frame.drop_duplicates(subset=["order_item_id"], keep="first")
        frame["order_id"] = frame["order_id"].map(
            lambda value: to_int(value, default=None)
        )
        frame = frame.dropna(subset=["order_id"])
        invalid_order = ~frame["order_id"].isin(valid_order_ids)
        for row_id in frame.loc[invalid_order, "order_item_id"]:
            self.tracker.record("order_items", row_id, "order_id",
                                "order_id has no matching order")
        frame = frame[~invalid_order]
        frame["product_id"] = frame["product_id"].map(
            lambda value: to_int(value, default=None)
        )
        invalid_product = ~frame["product_id"].isin(valid_product_ids)
        for row_id in frame.loc[invalid_product, "order_item_id"]:
            self.tracker.record("order_items", row_id, "product_id",
                                "product_id has no matching product")
        frame = frame[~invalid_product]
        frame["quantity"] = frame["quantity"].map(
            lambda value: to_int(value, default=1)
        )
        negative_qty = frame["quantity"] < 0
        self.tracker.record("order_items", None, "quantity",
                            f"{int(negative_qty.sum())} negative quantities "
                            "converted to absolute value")
        frame.loc[negative_qty, "quantity"] = (
            frame.loc[negative_qty, "quantity"].abs()
        )
        zero_qty = frame["quantity"] == 0
        self.tracker.record("order_items", None, "quantity",
                            f"{int(zero_qty.sum())} zero quantities replaced "
                            "with 1")
        frame.loc[zero_qty, "quantity"] = 1
        frame["unit_price"] = frame["unit_price"].map(
            lambda value: to_float(value)
        )
        frame["unit_price"] = frame["unit_price"].where(
            frame["unit_price"] > 0, 0.0
        )
        frame["discount"] = frame["discount"].map(
            lambda value: to_float(value)
        )
        over_100 = frame["discount"] > 1.0
        self.tracker.record("order_items", None, "discount",
                            f"{int(over_100.sum())} discounts over 100% "
                            "clamped to 0")
        frame.loc[over_100, "discount"] = 0.0
        negative_discount = frame["discount"] < 0
        self.tracker.record("order_items", None, "discount",
                            f"{int(negative_discount.sum())} negative "
                            "discounts clamped to 0")
        frame.loc[negative_discount, "discount"] = 0.0
        frame["line_total"] = (
            frame["quantity"] * frame["unit_price"] * (1 - frame["discount"])
        ).round(2)
        frame = frame.sort_values("order_item_id").reset_index(drop=True)

        frame["item_id"] = frame["order_item_id"]
        frame["discount_percent"] = frame["discount"]
        logger.info(
            "order_items: %s -> %s (dropped %s)",
            original, len(frame), original - len(frame),
        )
        return frame


    def validate_emails(self, frame: pd.DataFrame, path: Path) -> None:
        invalid = frame[~frame["email"].map(is_valid_email)]
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "E-Commerce Order Analytics System - Email Validation Report",
            "=" * 60,
            f"Total emails checked: {len(frame)}",
            f"Invalid emails: {len(invalid)}",
            "",
            "customer_id,email",
        ]
        for _, row in invalid.iterrows():
            lines.append(f"{row['customer_id']},{row['email']}")
        path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Wrote email validation report to %s", path)

    def check_referential_integrity(
        self,
        customers: pd.DataFrame,
        products: pd.DataFrame,
        orders: pd.DataFrame,
        order_items: pd.DataFrame,
        path: Path,
    ) -> None:
        customer_ids = set(customers["customer_id"])
        product_ids = set(products["product_id"])
        order_ids = set(orders["order_id"])

        orphan_orders = len(
            orders[~orders["customer_id"].isin(customer_ids)]
        )
        orphan_items_order = len(
            order_items[~order_items["order_id"].isin(order_ids)]
        )
        orphan_items_product = len(
            order_items[~order_items["product_id"].isin(product_ids)]
        )

        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "E-Commerce Order Analytics System - Referential Integrity Report",
            "=" * 60,
            "Orphan order rows (customer_id not in customers):",
            f"  {orphan_orders}",
            "Orphan order_item rows (order_id not in orders):",
            f"  {orphan_items_order}",
            "Orphan order_item rows (product_id not in products):",
            f"  {orphan_items_product}",
            "",
            "Final entity sizes:",
            f"  customers:   {len(customers)}",
            f"  products:    {len(products)}",
            f"  orders:      {len(orders)}",
            f"  order_items: {len(order_items)}",
        ]
        path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Wrote referential integrity report to %s", path)

    def validation_summary(
        self, frames: dict[str, pd.DataFrame], path: Path
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "E-Commerce Order Analytics System - Validation Report",
            "=" * 60,
            f"{'Entity':<14} {'Rows':<8} {'Nulls':<8} {'Duplicates':<10}",
        ]
        for entity, frame in frames.items():
            nulls = int(frame.isna().sum().sum())
            duplicates = int(frame.duplicated().sum())
            lines.append(
                f"{entity:<14} {len(frame):<8} {nulls:<8} {duplicates:<10}"
            )
        path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Wrote validation report to %s", path)


    def run(
        self,
        raw_paths: dict[str, Path] | None = None,
        clean_paths: dict[str, Path] | None = None,
    ) -> dict[str, pd.DataFrame]:

        raw = raw_paths or {
            "customers": RAW_CUSTOMERS,
            "products": RAW_PRODUCTS,
            "orders": RAW_ORDERS,
            "order_items": RAW_ORDER_ITEMS,
        }
        clean = clean_paths or {
            "customers": CLEAN_CUSTOMERS,
            "products": CLEAN_PRODUCTS,
            "orders": CLEAN_ORDERS,
            "order_items": CLEAN_ORDER_ITEMS,
        }

        customers = self.clean_customers(read_frame(raw["customers"]))
        products = self.clean_products(read_frame(raw["products"]))
        orders = self.clean_orders(
            read_frame(raw["orders"]), set(customers["customer_id"])
        )
        order_items = self.clean_order_items(
            read_frame(raw["order_items"]),
            set(orders["order_id"]),
            set(products["product_id"]),
        )

        write_frame(customers, clean["customers"])
        write_frame(products, clean["products"])
        write_frame(orders, clean["orders"])
        write_frame(order_items, clean["order_items"])

        self.tracker.write_report(CLEANING_REPORT)
        self.validate_emails(customers, EMAIL_REPORT)
        self.check_referential_integrity(
            customers, products, orders, order_items,
            REFERENTIAL_INTEGRITY_REPORT,
        )
        self.validation_summary(
            {
                "customers": customers,
                "products": products,
                "orders": orders,
                "order_items": order_items,
            },
            VALIDATION_REPORT,
        )

        return {
            "customers": customers,
            "products": products,
            "orders": orders,
            "order_items": order_items,
        }

def main() -> None:

    logging.basicConfig(level=logging.INFO)
    cleaner = DataCleaner()
    cleaner.run()

if __name__ == "__main__":
    main()