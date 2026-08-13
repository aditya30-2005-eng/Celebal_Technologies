
import random
import logging
from datetime import date, timedelta

import pandas as pd
from faker import Faker

from config import (
    RAW_CUSTOMERS,
    RAW_PRODUCTS,
    RAW_ORDERS,
    RAW_ORDER_ITEMS,
    N_CUSTOMERS,
    N_PRODUCTS,
    N_ORDERS,
    N_ORDER_ITEMS,
    MIN_ITEMS_PER_ORDER,
    MAX_ITEMS_PER_ORDER,
    MIN_PRICE,
    MAX_PRICE,
    ORDER_STATUSES,
    PAYMENT_METHODS,
    CATEGORIES,
    REGIONS,
    PRODUCT_NAME_BANK,
    BRANDS,
    CITIES,
    CUSTOMER_TYPES,
    CATEGORY_SUBCATEGORIES,
    RANDOM_SEED,
)
from scripts.utils import write_frame

logger = logging.getLogger(__name__)

_UNICODE_SAMPLES = ("✓", "™", "Δ", "Ω", "ğ", "ñ", "中", "😀")

class DataGenerator:

    def __init__(
        self,
        seed: int = RANDOM_SEED,
        n_customers: int = N_CUSTOMERS,
        n_products: int = N_PRODUCTS,
        n_orders: int = N_ORDERS,
        n_order_items: int = N_ORDER_ITEMS,
    ) -> None:
        self.random = random.Random(seed)
        self.faker = Faker(seed)
        self.faker.seed_instance(seed)
        self.n_customers = n_customers
        self.n_products = n_products
        self.n_orders = n_orders
        self.n_order_items = n_order_items


    def _pick(self, ratio: float) -> bool:
        return self.random.random() < ratio

    def _maybe_string(self, ratio: float, value: str) -> str:
        if not self._pick(ratio):
            return value
        kind = self.random.random()
        if kind < 0.30:
            return ""
        if kind < 0.55:
            return "   " + value + "   "
        if kind < 0.80:
            return value.swapcase()
        return value.upper()

    def _maybe_unicode(self, ratio: float, value: str) -> str:
        if not self._pick(ratio):
            return value
        return value + self.random.choice(_UNICODE_SAMPLES)

    def _maybe_email(self, ratio: float, email: str) -> str:

        if not self._pick(ratio):
            return email
        corruption = self.random.randint(0, 3)
        if corruption == 0:
            return "not-an-email"
        if corruption == 1:
            return email.replace("@", "")
        if corruption == 2:
            return email.replace("@", "").replace(".", "x")
        return "user" + self.random.choice(["", "123", "id"]) + " email"

    def _maybe_customer_id(self, ratio: float,
                           valid_ids: list[int]) -> int | None:

        if not self._pick(ratio):
            return self.random.choice(valid_ids)
        kind = self.random.random()
        if kind < 0.60:
            return max(valid_ids) + self.random.randint(1, 100)
        return 0

    def _maybe_date(self, ratio: float, value: date) -> date | str:
        if not self._pick(ratio):
            return value
        kind = self.random.random()
        if kind < 0.4:
            return value.strftime("%d-%m-%Y")
        if kind < 0.6:
            return value.strftime("%m/%d/%Y")
        if kind < 0.8:
            return value.strftime("%Y/%m/%d")
        return value.strftime("%d-%b-%Y")

    def _maybe_future_date(self, ratio: float, value: date) -> date:
        if not self._pick(ratio):
            return value
        return value + timedelta(days=self.random.randint(1, 90))

    def _maybe_wrong_datatype(self, ratio: float, value) -> object:
        if not self._pick(ratio):
            return value
        return self.random.choice(
            [str(value), f"{value}.0", None, f"o{value}", -abs(value)]
        )


    def _customer_row(self, customer_id: int) -> dict:
        first = self.faker.first_name()
        last = self.faker.last_name()
        name = f"{first} {last}"
        joined = self.faker.date_between(start_date="-4y", end_date="today")
        return {
            "customer_id": customer_id,
            "name": self._maybe_unicode(
                0.02, self._maybe_string(0.10, name)
            ),
            "email": self.faker.email(domain="example.com"),
            "customer_type": self.random.choice(CUSTOMER_TYPES),
            "region": self._maybe_string(0.05, self.random.choice(REGIONS)),
            "city": self._maybe_string(0.05, self.random.choice(CITIES)),
            "joined_date": self._maybe_date(0.03, joined),
        }

    def _product_row(self, product_id: int) -> dict:
        name = self.random.choice(PRODUCT_NAME_BANK)
        base_price = round(self.random.uniform(MIN_PRICE, MAX_PRICE), 2)
        category = self.random.choice(CATEGORIES)
        subcategory = self.random.choice(
            CATEGORY_SUBCATEGORIES[category]
        )
        price: object
        if self._pick(0.02):
            price = None
        else:
            price = self._maybe_wrong_datatype(0.01, base_price)
        row: dict = {
            "product_id": product_id,
            "product_name": self._maybe_unicode(
                0.02, self._maybe_string(0.20, name)
            ),
            "category": self._maybe_string(0.05, category),
            "subcategory": self._maybe_string(0.05, subcategory),
            "brand": self._maybe_string(0.05, self.random.choice(BRANDS)),
            "price": price,
            "cost_price": round(base_price * self.random.uniform(0.40, 0.70), 2),
            "stock_quantity": self.random.randint(0, 500),
        }
        if self._pick(0.05):
            row["product_id"] = f"000{product_id}"
        return row

    def _order_row(self, order_id: int, valid_ids: list[int]) -> dict:
        status: object = self.random.choice(ORDER_STATUSES)
        if self._pick(0.02):
            status = self.faker.word() + self.faker.word()
        order_date = self.faker.date_between(
            start_date="-4y", end_date="today"
        )
        order_date = self._maybe_future_date(0.03, order_date)
        order_date = self._maybe_date(0.04, order_date)
        return {
            "order_id": order_id,
            "customer_id": self._maybe_customer_id(0.05, valid_ids),
            "order_date": order_date,
            "status": status,
            "payment_method": self._maybe_string(
                0.05, self.random.choice(PAYMENT_METHODS)
            ),
            "shipping_region": self._maybe_string(
                0.05, self.random.choice(REGIONS)
            ),
        }

    def _order_item_row(self, order_item_id: int, order_id: int,
                        valid_product_ids: list[int]) -> dict:
        product_id = self.random.choice(valid_product_ids)
        if self._pick(0.02):
            product_id = max(valid_product_ids) + self.random.randint(1, 25)
        quantity: object = self.random.randint(1, 8)
        if self._pick(0.02):
            quantity = 0
        discount: object = 0.0
        if self._pick(0.15):
            discount = round(self.random.uniform(0.05, 0.40), 2)
        if self._pick(0.02):
            discount = round(self.random.uniform(1.10, 1.90), 2)
        elif self._pick(0.01):
            discount = round(self.random.uniform(-0.10, -0.01), 2)
        return {
            "order_item_id": order_item_id,
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": round(self.random.uniform(MIN_PRICE, MAX_PRICE), 2),
            "discount": discount,
        }


    def _customers_frame(self) -> pd.DataFrame:
        ids = list(range(1, self.n_customers + 1))
        rows = [self._customer_row(identifier) for identifier in ids]
        for duplicate in self.random.sample(
            rows, int(self.n_customers * 0.03)
        ):
            rows.append(dict(duplicate))
        frame = pd.DataFrame(rows)


        corruption_count = round(self.n_customers * 0.02)
        corrupt_idx = self.random.sample(
            list(frame.index), corruption_count
        )
        for index in corrupt_idx:
            frame.at[index, "email"] = self._maybe_email(
                1.0, frame.at[index, "email"]
            )
        return frame

    def _products_frame(self) -> pd.DataFrame:
        ids = list(range(1, self.n_products + 1))
        rows = [self._product_row(identifier) for identifier in ids]
        for duplicate in self.random.sample(
            rows, int(self.n_products * 0.03)
        ):
            rows.append(dict(duplicate))
        return pd.DataFrame(rows)

    def _orders_frame(self) -> pd.DataFrame:
        customer_ids = list(range(1, self.n_customers + 1))
        rows = [
            self._order_row(order_id, customer_ids)
            for order_id in range(1, self.n_orders + 1)
        ]
        frame = pd.DataFrame(rows)

        corruption_count = round(self.n_orders * 0.05)
        corrupt_idx = self.random.sample(
            list(frame.index), corruption_count
        )
        for index in corrupt_idx:
            frame.at[index, "customer_id"] = None
        return frame

    def _order_items_frame(self) -> pd.DataFrame:
        product_ids = list(range(1, self.n_products + 1))
        rows: list[dict] = []
        item_counter = 1
        for order_id in range(1, self.n_orders + 1):
            item_count = self.random.randint(
                MIN_ITEMS_PER_ORDER, MAX_ITEMS_PER_ORDER
            )
            for _ in range(item_count):
                rows.append(
                    self._order_item_row(
                        item_counter, order_id, product_ids
                    )
                )
                item_counter += 1
        target = self.n_order_items
        while len(rows) < target:
            rows.append(
                self._order_item_row(
                    item_counter,
                    self.random.randint(1, self.n_orders),
                    product_ids,
                )
            )
            item_counter += 1
        if len(rows) > target:
            rows = rows[:target]
        frame = pd.DataFrame(rows)


        eligible = frame.index[frame["quantity"] > 0].tolist()
        corruption_count = round(self.n_order_items * 0.03)
        corrupt_idx = self.random.sample(eligible, corruption_count)
        for index in corrupt_idx:
            frame.at[index, "quantity"] = -frame.at[index, "quantity"]
        return frame


    def _data_quality_summary(self, customers, products, orders,
                              order_items) -> str:

        orders_total = len(orders)
        null_customer = (
            orders["customer_id"].isna()
            | (orders["customer_id"].astype(str).str.strip() == "")
        ).sum()

        items_total = len(order_items)
        quantities = pd.to_numeric(
            order_items["quantity"], errors="coerce"
        )
        negative_qty = int((quantities < 0).sum())

        customers_total = len(customers)
        invalid_emails = int(
            (~customers["email"].astype(str).str.contains("@")).sum()
        )

        invalid_dates = int(
            orders["order_date"].astype(str).str.match(
                r"^\d{2}-\d{2}-\d{4}$"
            ).sum()
        )

        def _duplicate_count(frame, subset) -> int:
            return int(frame.duplicated(subset=subset).sum())

        invalid_ids = int(
            (
                orders["customer_id"].notna()
                & ~orders["customer_id"].isin(customers["customer_id"])
            ).sum()
        )

        lines = [
            "RAW DATA QUALITY",
            "----------------",
            "Orders:",
            f"  Total:                 {orders_total}",
            f"  NULL customer_id:       {null_customer}",
            f"  Percentage:             {100.0 * null_customer / orders_total:.2f}%",
            "",
            "Order Items:",
            f"  Total:                 {items_total}",
            f"  Negative quantity:      {negative_qty}",
            f"  Percentage:             {100.0 * negative_qty / items_total:.2f}%",
            "",
            "Customers:",
            f"  Total:                 {customers_total}",
            f"  Invalid emails:         {invalid_emails}",
            f"  Percentage:             {100.0 * invalid_emails / customers_total:.2f}%",
            "",
            f"Invalid dates:            {invalid_dates}",
            f"Duplicate rows:           "
            f"{_duplicate_count(customers, ['customer_id'])}",
            f"Invalid IDs:              {invalid_ids}",
        ]
        return "\n".join(lines)


    def generate(self, print_summary: bool = True) -> None:

        customers = self._customers_frame()
        products = self._products_frame()
        orders = self._orders_frame()
        order_items = self._order_items_frame()

        write_frame(customers, RAW_CUSTOMERS)
        write_frame(products, RAW_PRODUCTS)
        write_frame(orders, RAW_ORDERS)
        write_frame(order_items, RAW_ORDER_ITEMS)

        logger.info(
            "Raw datasets generated: customers=%s products=%s orders=%s "
            "order_items=%s",
            len(customers),
            len(products),
            len(orders),
            len(order_items),
        )

        if print_summary:
            print("\n" + self._data_quality_summary(
                customers, products, orders, order_items
            ) + "\n")

def main() -> None:

    logging.basicConfig(level=logging.INFO)
    DataGenerator().generate()

if __name__ == "__main__":
    main()