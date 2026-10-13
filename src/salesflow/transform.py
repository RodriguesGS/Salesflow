import logging

logger = logging.getLogger(__name__)

def transform(df):

    logger.info("Iniciando transformação")
    
    df = df.copy