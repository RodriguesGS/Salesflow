import logging
import sys

from time import perf_counter

from salesflow.contract import DataQualityError, check_raw
from salesflow.extract import extract
from salesflow.transform import transform
from salesflow.load import load

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("salesflow")


def main() -> None:
    
    start_time = perf_counter()
    
    logger.info("Salesflow pipeline started")

    raw = extract()
    check_raw(raw)
    
    df_clean, df_rejected = transform(raw)
    load(df_clean, df_rejected)
    
    elapsed_time = perf_counter() - start_time
    
    logger.info(
        "Salesflow pipeline completed successfully | Duration: %.2f seconds",
        elapsed_time,
    )
    
if __name__ == "__main__":
    try:
        main()
    except DataQualityError:
        logger.exception("Pipeline stopped due to a data quality error")
        sys.exit(2)
    except Exception:
        logger.exception("Pipeline failed due to an unexpected error")
        sys.exit(1)
        