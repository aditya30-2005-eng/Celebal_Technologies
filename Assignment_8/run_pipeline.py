
import logging
import sys

from config import configure_logging, ensure_directories
from scripts.build_database import DatabaseBuilder
from scripts.clean_data import DataCleaner
from scripts.generate_data import DataGenerator
from scripts.run_sql_queries import SqlQueryRunner

logger = logging.getLogger(__name__)

def run_pipeline() -> int:

    configure_logging()
    ensure_directories()

    logger.info("Step 1/4: Generating raw datasets")
    DataGenerator().generate()

    logger.info("Step 2/4: Cleaning datasets")
    DataCleaner().run()

    logger.info("Step 3/4: Building database")
    builder = DatabaseBuilder()
    if not builder.build():
        logger.error("Database build verification failed")
        return 1

    logger.info("Step 4/4: Running SQL analytics")
    failed = SqlQueryRunner().run_all()
    if failed:
        logger.warning("Some SQL files failed to execute")

    logger.info("Pipeline completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(run_pipeline())