import pandas as pd
import logging

from collections import Counter
from salesflow.contract import DataQualityError

logger = logging.getLogger(__name__)


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    
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

def normalize_null(df: pd.DataFrame) -> pd.DataFrame:
    
    return df.replace(["", "ERROR", "UNKNOWN"], pd.NA)

def cast_types(df: pd.DataFrame) -> pd.DataFrame:
    
    df = df.copy()
    
    df["quantity"] = pd.to_numeric(df["quantity"]).astype("Int64")
    df["price_per_unit"] = pd.to_numeric(df["price_per_unit"])
    df["total_spent"] = pd.to_numeric(df["total_spent"])
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], format="%Y-%m-%d")
    
    logger.info("Type conversion completed for 4 columns")

    return df

def missing_data(df: pd.DataFrame) -> None:
    
    m = df.isna().sum()
    m = m[m > 0]
    
    report = pd.DataFrame({
        "qtd": m,
        "%": (m / len(df) * 100).round(1)
    })
    
    logger.info(f"Missing values by column: \n{report.to_string()}")

    for i, pct in report["%"].items():
        
        if pct > 10:
            logger.warning(f"Column {i} has {pct:.2f}% missing values")
    
def build_menu(df: pd.DataFrame) -> dict[str, float]:
    
    valid = df.dropna(subset=["item", "price_per_unit"])
    
    price_counts = valid.groupby("item")["price_per_unit"].nunique()
    inconsistent_items = price_counts[price_counts > 1].index.tolist()
    
    if inconsistent_items:
        raise DataQualityError(
            f"Items with multiple prices: {inconsistent_items}"
        )

    logger.info("Data consistency validated: each item has one price")
    
    menu = valid.groupby("item")["price_per_unit"].first()

    return {str(item): float(price) for item, price in menu.items()}

def fill_price_from_item(df: pd.DataFrame, menu: dict[str, float]) -> pd.DataFrame:
    
    df = df.copy()
    
    mask = df["price_per_unit"].isna() & df["item"].notna()
    df.loc[mask, "price_per_unit"] = df.loc[mask, "item"].map(menu)
    
    return df

def fill_item_from_price(df: pd.DataFrame, menu: dict[str, float]) -> pd.DataFrame:
    
    df = df.copy()
    
    counts = Counter(menu.values())
    
    inverted = {}
    
    for i, p in menu.items():
        if counts[p] == 1:
            inverted[p] = i
        
    mask = df["item"].isna() & df["price_per_unit"].notna()
    df.loc[mask, "item"] = df.loc[mask, "price_per_unit"].map(inverted)
    
    return df

def fill_values(df: pd.DataFrame) -> pd.DataFrame:
    
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

def resolve_until_stable(df: pd.DataFrame, menu: dict[str, float]) -> pd.DataFrame:
    
    columns = ["item", "quantity", "price_per_unit", "total_spent"]
    before = df[columns].isna().sum()
    previous = before.sum()
    i = 0
    
    while True:
        
        i += 1
        
        df = fill_price_from_item(df, menu)
        df = fill_item_from_price(df, menu)
        df = fill_values(df)
        
        current = df[columns].isna().sum().sum()
        
        logger.info(f"Round {i}: {previous - current} values recovered | {current} missing values remaining")
          
        if current == previous:
            break
        
        previous = current
        
    after = df[columns].isna().sum()
 
    report = pd.DataFrame({
        "before": before,
        "recovered": before - after,
        "remaining": after,
    })
 
    logger.info(f"Recovery summary by column:\n{report.to_string()}")
    logger.info(f"Total values recovered: {before.sum() - after.sum()} of {before.sum()} {(before.sum() - after.sum()) / before.sum() * 100:.2f}%")
 
    return df 

def fill_unknown(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    unknown_counts = df[["item", "payment_method", "location"]].isna().sum()
    logger.info("Values to mark as Unknown:\n%s", unknown_counts.to_string())
 
    for i in ["item", "payment_method", "location"]:
        df[i] = df[i].fillna("Unknown")
 
    logger.info("Missing transaction dates preserved: %s", df["transaction_date"].isna().sum())
 
    return df

def split_rejected(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    
    mask = df["quantity"].isna() | df["price_per_unit"].isna() | df["total_spent"].isna()
 
    rejected = df.loc[mask].copy()
    rejected["reject_reason"] = "Unrecoverable required values"
 
    clean = df.loc[~mask].copy()
 
    logger.info("Clean records: %s | Rejected records:: %s", len(clean), len(rejected))
 
    if not rejected.empty:
        logger.warning("Rejected records by reason:\n%s", rejected["reject_reason"].value_counts().to_string(header=False))
 
    return clean, rejected

def transform(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:

    logger.info("Starting data transformation")
    
    logger.info("Running initial diagnostics")
    df = rename_columns(df)
    df = normalize_null(df)
    df = cast_types(df)
    missing_data(df)
    
    logger.info("Starting rule-based value recovery")
    menu = build_menu(df)
    df = resolve_until_stable(df, menu)
    
    logger.info("Handling unknown categorical values")
    
    df = fill_unknown(df)
    
    logger.info("Splitting clean and rejected records")
    
    clean, rejected = split_rejected(df)
    
    return clean, rejected