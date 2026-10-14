import logging
import kagglehub
import os
import pandas as pd

from kagglehub import KaggleDatasetAdapter

logger = logging.getLogger(__name__)

def extract() -> pd.DataFrame:
    
    logger.info("Starting data extraction")
    
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training",
        path="dirty_cafe_sales.csv",
        pandas_kwargs={"dtype": "str", "keep_default_na": False}
    )
    
    df.to_csv("data/raw/data.csv", index=False)
    
    logger.info(f"Raw dataset saved:: data/raw/data.csv | {(os.path.getsize("data/raw/data.csv")) / (1024 * 1024):.2f} MB")
    logger.info(f"Dataset volume: {len(df)} rows | {len(df.columns)} columns")
    
    return df
