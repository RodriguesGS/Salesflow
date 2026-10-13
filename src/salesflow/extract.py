import logging
import kagglehub

from kagglehub import KaggleDatasetAdapter

logger = logging.getLogger(__name__)

def extract():
    
    logger.info("Iniciando extração dos dados")
    
    try: 
        df = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            "ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training",
            path="dirty_cafe_sales.csv",
        )
        
        df.to_csv("data/raw/dirty_cafe_sales.csv", index=False)
        
        logger.info(f"Extração concluída: {len(df)} registros")
        
        return df
    
    except Exception:
        logging.error("Erro durante a extração dos dados")
        raise
