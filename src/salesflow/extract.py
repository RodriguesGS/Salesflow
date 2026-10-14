import logging
import kagglehub

from kagglehub import KaggleDatasetAdapter

logger = logging.getLogger(__name__)

def extract():
    
    logger.info("Iniciando extração dos dados")
    
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training",
        path="dirty_cafe_sales.csv",
        pandas_kwargs={"dtype": "str", "keep_default_na": False}
    )
    
    df.to_csv("data/raw/dirty_cafe_sales.csv", index=False)
    
    return df
