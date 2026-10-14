import logging
import pandas as pd

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = {
    "Transaction ID",
    "Item",
    "Quantity",
    "Price Per Unit",
    "Total Spent",
    "Payment Method",
    "Location",
    "Transaction Date"
}

class DataQualityError(Exception):
    pass
    
def check_raw(df):
    
    logger.info("Starting contract validation")
    
    if df.empty:
        raise DataQualityError("The dataframe is empty")
    
    missing_columns = EXPECTED_COLUMNS - set(df.columns)
    if missing_columns:
        raise DataQualityError(f"Missing columns: {sorted(missing_columns)}")
    
    duplicated = df["Transaction ID"].duplicated().sum()
    if duplicated > 0:
        raise DataQualityError(f"transaction_id has {duplicated} duplicated values")
    
    f = len(EXPECTED_COLUMNS & set(df.columns))

    logger.info(f"Schema OK: {f}/{len(EXPECTED_COLUMNS)} expected columns")
    logger.info("Uniqueness OK: transaction_id %s/%s unique", df["Transaction ID"].nunique(), len(df))
    