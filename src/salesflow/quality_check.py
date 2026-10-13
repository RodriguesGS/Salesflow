import logging
import pandas as pd

logger = logging.getLogger(__name__)

def check_empty(df):
    
    if df.empty:
        raise ValueError("O Dataframe está vazio")