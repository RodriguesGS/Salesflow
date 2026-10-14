import pandas as pd
import logging

logger = logging.getLogger(__name__)


def rename_columns(df):
    
    columns = {
        "Transaction ID": "transaction_id",
        "Item": "item",
        "Quantity": "quantity",
        "Price Per Unit": "price_per_unit",
        "Total Spent": "total_spent",
        "Payment Method": "payment_method",
        "Location": "location",
        "Transaction Date": "transaction_date",
    }
    
    df = df.rename(columns=columns)
    
    return df

def normalize_null(df):
    
    return df.replace(["", "ERROR", "UNKNOWN"], pd.NA)

def cast_types(df):
    
    df = df.copy()
    
    df["quantity"] = pd.to_numeric(df["quantity"]).astype("Int64")
    df["price_per_unit"] = pd.to_numeric(df["price_per_unit"])
    df["total_spent"] = pd.to_numeric(df["total_spent"])
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], format="%Y-%m-%d")

    return df


def transform(df):

    logger.info("Iniciando transformação")
    
    df = rename_columns(df)
    df = normalize_null(df)
    df = cast_types(df)
    
    return df