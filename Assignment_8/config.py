
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path


BASE_DIR: Path = Path(__file__).resolve().parent

DATA_DIR: Path = BASE_DIR / "data"
RAW_DIR: Path = DATA_DIR / "raw"
CLEAN_DIR: Path = DATA_DIR / "cleaned"

LOG_DIR: Path = BASE_DIR / "logs"
REPORT_DIR: Path = BASE_DIR / "reports"
DB_DIR: Path = BASE_DIR / "database"
OUTPUT_DIR: Path = BASE_DIR / "output"
SQL_DIR: Path = BASE_DIR / "sql"

DB_PATH: Path = DB_DIR / "ecommerce.db"

LOG_FILE: Path = LOG_DIR / "project.log"

OUTPUT_CSV_DIR: Path = OUTPUT_DIR / "csv"
OUTPUT_TXT_DIR: Path = OUTPUT_DIR / "txt"
SAMPLE_OUTPUT_DIR: Path = OUTPUT_DIR / "sample_outputs"
SCREENSHOT_DIR: Path = OUTPUT_DIR / "screenshots"

RAW_CUSTOMERS: Path = RAW_DIR / "customers.csv"
RAW_PRODUCTS: Path = RAW_DIR / "products.csv"
RAW_ORDERS: Path = RAW_DIR / "orders.csv"
RAW_ORDER_ITEMS: Path = RAW_DIR / "order_items.csv"

CLEAN_CUSTOMERS: Path = CLEAN_DIR / "customers_clean.csv"
CLEAN_PRODUCTS: Path = CLEAN_DIR / "products_clean.csv"
CLEAN_ORDERS: Path = CLEAN_DIR / "orders_clean.csv"
CLEAN_ORDER_ITEMS: Path = CLEAN_DIR / "order_items_clean.csv"

CLEANING_REPORT: Path = REPORT_DIR / "cleaning_report.txt"
VALIDATION_REPORT: Path = REPORT_DIR / "validation_report.txt"
EMAIL_REPORT: Path = REPORT_DIR / "email_report.txt"
REFERENTIAL_INTEGRITY_REPORT: Path = REPORT_DIR / "referential_integrity_report.txt"


N_CUSTOMERS: int = 800
N_PRODUCTS: int = 500
N_ORDERS: int = 3500
N_ORDER_ITEMS: int = 12000

MIN_ITEMS_PER_ORDER: int = 1
MAX_ITEMS_PER_ORDER: int = 6

MIN_PRICE: float = 4.99
MAX_PRICE: float = 1499.99


NULL_CUSTOMER_ID_RATIO: float = 0.05
INVALID_EMAIL_RATIO: float = 0.02
DUPLICATE_ROW_RATIO: float = 0.03
INVALID_FK_RATIO: float = 0.02
FUTURE_DATE_RATIO: float = 0.03
WRONG_DATE_FORMAT_RATIO: float = 0.04
EMPTY_STRING_RATIO: float = 0.02
WHITESPACE_RATIO: float = 0.03
MIXED_CASE_RATIO: float = 0.20
MISSING_PRICE_RATIO: float = 0.02
DISCOUNT_OVER_100_RATIO: float = 0.02
DISCOUNT_NEGATIVE_RATIO: float = 0.01
QUANTITY_ZERO_RATIO: float = 0.02
NEGATIVE_QUANTITY_RATIO: float = 0.01
INVALID_STATUS_RATIO: float = 0.02
INVALID_CATEGORY_RATIO: float = 0.02
INVALID_REGION_RATIO: float = 0.02
DUPLICATE_ID_RATIO: float = 0.02
UNICODE_RATIO: float = 0.02
LEADING_ZERO_RATIO: float = 0.05
WRONG_DATATYPE_RATIO: float = 0.02
MISSING_VALUE_RATIO: float = 0.02

RANDOM_SEED: int = 42


ORDER_STATUSES: list[str] = [
    "PENDING",
    "PROCESSING",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED",
    "RETURNED",
    "REFUNDED",
]

PAYMENT_METHODS: list[str] = [
    "credit_card",
    "debit_card",
    "paypal",
    "bank_transfer",
    "cash_on_delivery",
    "gift_card",
]

CATEGORIES: list[str] = [
    "Electronics",
    "Clothing",
    "Home & Kitchen",
    "Books",
    "Sports",
    "Beauty",
    "Toys",
    "Grocery",
    "Automotive",
    "Office",
]

REGIONS: list[str] = [
    "North America",
    "South America",
    "Europe",
    "Asia Pacific",
    "Middle East",
    "Africa",
]

PRODUCT_NAME_BANK: list[str] = [
    "Wireless Mouse",
    "Mechanical Keyboard",
    "USB-C Hub",
    "Noise Cancelling Headphones",
    "4K Monitor",
    "Laptop Stand",
    "Webcam HD",
    "Bluetooth Speaker",
    "External SSD 1TB",
    "Portable Charger",
    "Desk Lamp",
    "Ergonomic Chair",
    "Standing Desk",
    "Cable Organizer",
    "Surge Protector",
    "Cotton T-Shirt",
    "Denim Jeans",
    "Running Shoes",
    "Leather Belt",
    "Winter Jacket",
    "Wool Scarf",
    "Sun Glasses",
    "Baseball Cap",
    "Dress Shirt",
    "Chino Pants",
    "Cast Iron Pan",
    "Chef Knife",
    "Coffee Maker",
    "Blender",
    "Air Fryer",
    "Rice Cooker",
    "Toaster",
    "Kettle",
    "Fiction Novel",
    "Cookbook",
    "Self Help Guide",
    "History Book",
    "Biography",
    "Science Journal",
    "Yoga Mat",
    "Dumbbell Set",
    "Treadmill",
    "Football",
    "Basketball",
    "Tennis Racket",
    "Moisturizer",
    "Shampoo",
    "Perfume",
    "Sunscreen",
    "Lipstick",
    "Building Blocks",
    "Remote Control Car",
    "Board Game",
    "Doll House",
    "Puzzle Set",
    "Organic Rice",
    "Olive Oil",
    "Green Tea",
    "Honey Jar",
    "Almonds",
    "Car Polish",
    "Air Freshener",
    "Engine Oil",
    "Tire Cleaner",
    "Wiper Blades",
    "Notebook",
    "Ballpoint Pens",
    "Stapler",
    "Desk Organizer",
    "Paper Clips",
]

BRANDS: list[str] = [
    "NovaTech",
    "Apex",
    "UrbanFit",
    "HomeCraft",
    "ReadWell",
    "PureLife",
    "SpeedPro",
    "GreenLeaf",
    "Optima",
    "Vertex",
]

CITIES: list[str] = [
    "New York",
    "Los Angeles",
    "Chicago",
    "Houston",
    "Phoenix",
    "London",
    "Paris",
    "Berlin",
    "Tokyo",
    "Sydney",
    "Toronto",
    "Mumbai",
    "Sao Paulo",
    "Cape Town",
    "Dubai",
    "Singapore",
]

CUSTOMER_TYPES: list[str] = [
    "REGULAR",
    "PREMIUM",
    "VIP",
    "NEW",
]


CATEGORY_SUBCATEGORIES: dict[str, list[str]] = {
    "Electronics": ["Audio", "Computing", "Accessories", "Displays"],
    "Clothing": ["Men", "Women", "Footwear", "Accessories"],
    "Home & Kitchen": ["Cookware", "Appliances", "Storage", "Decor"],
    "Books": ["Fiction", "Non-Fiction", "Reference", "Children"],
    "Sports": ["Fitness", "Outdoor", "Team", "Equipment"],
    "Beauty": ["Skincare", "Haircare", "Fragrance", "Makeup"],
    "Toys": ["Building", "Vehicles", "Games", "Figures"],
    "Grocery": ["Pantry", "Beverages", "Snacks", "Organic"],
    "Automotive": ["Care", "Interior", "Maintenance", "Parts"],
    "Office": ["Stationery", "Furniture", "Supplies", "Equipment"],
}


def configure_logging() -> None:

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

@dataclass(frozen=True)
class ReportConfig:

    report: str = ""
    customer_id: int | None = None
    category: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    export_format: str | None = None

def ensure_directories() -> None:

    directories = [
        DATA_DIR,
        RAW_DIR,
        CLEAN_DIR,
        LOG_DIR,
        REPORT_DIR,
        DB_DIR,
        OUTPUT_DIR,
        OUTPUT_CSV_DIR,
        OUTPUT_TXT_DIR,
        SAMPLE_OUTPUT_DIR,
        SCREENSHOT_DIR,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
