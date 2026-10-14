import pandas as pd
import logging

from collections import Counter
from salesflow.contract import DataQualityError

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

def build_menu(df):
    
    valid = df.dropna(subset=["item", "price_per_unit"])
    
    count_price = valid.groupby("item")["price_per_unit"].nunique()
    
    if (count_price > 1).any():
        duplicated_items = count_price[count_price > 1].index.tolist()
        raise DataQualityError(f"Itens com mais de um preço: {duplicated_items}")

    return valid.groupby("item")["price_per_unit"].first().to_dict() 

def fill_price_from_item(df, menu):
    
    df = df.copy()
    
    mask = df["price_per_unit"].isna() & df["item"].notna()
    df.loc[mask, "price_per_unit"] = df.loc[mask, "item"].map(menu)
    
    return df

def fill_item_from_price(df, menu):
    
    df = df.copy()
    
    counts = Counter(menu.values())
    
    inverted = {}
    
    for i, p in menu.items():
        if counts[p] == 1:
            inverted[p] = i
        
    mask = df["item"].isna() & df["price_per_unit"].notna()
    df.loc[mask, "item"] = df.loc[mask, "price_per_unit"].map(inverted)
    
    return df

def fill_values(df):
    
    df = df.copy()
    
    q = df["quantity"]
    p = df["price_per_unit"]
    t = df["total_spent"]
    
    mask = t.isna() & q.notna() & p.notna()
    df.loc[mask, "total_spent"] = q[mask] * p[mask]
    
    mask = p.isna() & t.notna() & q.notna()
    df.loc[mask, "price_per_unit"] = t[mask] / q[mask]
    
    mask = q.isna() & p.notna() & t.notna()
    task =  t[mask] / p[mask]
    value_pass = (task % 1 == 0) & task.between(1, 5)
    df.loc[task[value_pass].index, "quantity"] = task[value_pass].astype("Int64")
    
    return df

def resolve_until_stable(df, menu):
    
    columns = ["item", "quantity", "price_per_unit", "total_spent"]
    previous = None
    i = 0
    
    while True:
        
        i += 1
        
        df = fill_price_from_item(df, menu)
        df = fill_item_from_price(df, menu)
        df = fill_values(df)
        
        current = df[columns].isna().sum().sum()
        
        logger.info("Rodada %s: %s nulos restantes", i, current)
          
        if current == previous:
            break
        
        previous = current
            
    return df

def fill_unknown(df):
    df = df.copy()
    
    for i in ["item", "payment_method", "location"]:
        df[i] = df[i].fillna("Unknown")
        
    return df

def split_rejected(df):
    
    mask = df["quantity"].isna() | df["price_per_unit"].isna() | df["total_spent"].isna()

    rejected = df[mask].copy()
    rejected["reject_reason"] = "tríade irrecuperável"

    clean = df[~mask]

    return clean, rejected

def transform(df):

    logger.info("Iniciando transformação")
    
    df = rename_columns(df)
    df = normalize_null(df)
    df = cast_types(df)
    
    menu = build_menu(df)
    logger.info("Cardápio montado: %s", menu)
    
    df = resolve_until_stable(df, menu)
    
    df = fill_unknown(df)
    
    clean, rejected = split_rejected(df)
    
    logger.info("Transformação concluída: %s limpas, %s rejeitadas", len(clean), len(rejected))
    
    return clean, rejected