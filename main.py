import logging
import sys

from salesflow.contract import DataQualityError, check_raw
from salesflow.extract import extract
from salesflow.transform import transform

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def main():
    
    logger.info("Iniciando Pipeline")
    

    raw = extract()
    logger.info("Extração concluída: %s linhas, %s colunas", *raw.shape)
    
    check_raw(raw)
    logger.info("Contrato de entrada OK")
    
    processed = transform(raw)

    print(processed.dtypes)
    print(processed.isna().sum())
    
    
if __name__ == "__main__":
    try:
        main()
    except DataQualityError:
        logger.exception("Pipeline interrompida por violacao de contrato")
        sys.exit(2)
    except Exception:
        logger.exception("Pipeline falhou por erro inesperado")
        sys.exit(1)
        