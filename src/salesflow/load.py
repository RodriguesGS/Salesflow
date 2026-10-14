import logging

logger = logging.getLogger(__name__)


def load(clean, rejected):
    
    clean.to_parquet("data/processed/cafe_sales.parquet", index=False)
    
    rejected.to_csv("data/rejected/cafe_sales_rejected.csv", index=False)
    
    logger.info("Gravadas %s linhas limpas e %s rejeitadas", len(clean), len(rejected))
