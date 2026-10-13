import logging

from salesflow.extract import extract
from salesflow.transform import transform
from salesflow.quality_check import check_empty

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def main():
    
    logger.info("Iniciando Pipeline")
    
    try:
        raw = extract()
        logger.info("Extração concluída")
        
        check_empty(raw)
        
        processed = transform(raw)
    except Exception:
        logger.exception("Falha durante a execução do pipeline")
    
    
if __name__ == "__main__":
    main()