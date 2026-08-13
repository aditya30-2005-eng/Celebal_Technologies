
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import DB_DIR, ensure_directories
from scripts.build_database import DatabaseBuilder
from scripts.clean_data import DataCleaner
from scripts.generate_data import DataGenerator

ensure_directories()

def _write_frame(frame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8")

@pytest.fixture(scope="session")
def project_root() -> Path:

    return PROJECT_ROOT

@pytest.fixture(scope="session")
def work_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:

    root = tmp_path_factory.mktemp("analytics")
    (root / "raw").mkdir(parents=True, exist_ok=True)
    (root / "cleaned").mkdir(parents=True, exist_ok=True)
    (root / "database").mkdir(parents=True, exist_ok=True)
    return root

@pytest.fixture(scope="session")
def generator() -> DataGenerator:

    return DataGenerator(
        seed=7,
        n_customers=60,
        n_products=40,
        n_orders=120,
        n_order_items=300,
    )

@pytest.fixture(scope="session")
def synthetic_paths(work_dir: Path, generator: DataGenerator) -> dict[str, Path]:

    paths = {
        "customers": work_dir / "raw" / "customers.csv",
        "products": work_dir / "raw" / "products.csv",
        "orders": work_dir / "raw" / "orders.csv",
        "order_items": work_dir / "raw" / "order_items.csv",
    }

    _write_frame(generator._customers_frame(), paths["customers"])
    _write_frame(generator._products_frame(), paths["products"])
    _write_frame(generator._orders_frame(), paths["orders"])
    _write_frame(generator._order_items_frame(), paths["order_items"])
    return paths

@pytest.fixture(scope="session")
def cleaned_frames(
    synthetic_paths: dict[str, Path], work_dir: Path
) -> dict[str, pd.DataFrame]:

    clean_paths = {
        "customers": work_dir / "cleaned" / "customers_clean.csv",
        "products": work_dir / "cleaned" / "products_clean.csv",
        "orders": work_dir / "cleaned" / "orders_clean.csv",
        "order_items": work_dir / "cleaned" / "order_items_clean.csv",
    }
    cleaner = DataCleaner()
    return cleaner.run(
        raw_paths=synthetic_paths,
        clean_paths=clean_paths,
    )

@pytest.fixture(scope="session")
def test_db_path(work_dir: Path) -> Path:

    return work_dir / "database" / "test_ecommerce.db"

@pytest.fixture(scope="session")
def built_database(
    cleaned_frames: dict[str, pd.DataFrame],
    test_db_path: Path,
    work_dir: Path,
) -> Path:

    clean_paths = {
        "customers": work_dir / "cleaned" / "customers_clean.csv",
        "products": work_dir / "cleaned" / "products_clean.csv",
        "orders": work_dir / "cleaned" / "orders_clean.csv",
        "order_items": work_dir / "cleaned" / "order_items_clean.csv",
    }
    builder = DatabaseBuilder(db_path=test_db_path)
    success = builder.build(clean_paths=clean_paths)
    assert success
    return test_db_path
