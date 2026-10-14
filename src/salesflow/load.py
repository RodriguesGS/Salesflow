import logging
import pandas as pd

logger = logging.getLogger(__name__)


def load(clean: pd.DataFrame, rejected: pd.DataFrame) -> None:
    
    logger.info("Starting data load")
    
    clean.to_parquet("data/processed/sales.parquet", index=False)
    rejected.to_csv("data/rejected/sales_rejected.csv", index=False)

    logger.info(f"data/processed/sales.parquet: {len(clean)} rows")
    logger.info(f"data/processed/sales_rejected.csv: {len(rejected)} rows")
