EXPECTED_COLUMNS = {
    "Transaction ID",
    "Item",
    "Quantity",
    "Price Per Unit",
    "Total Spent",
    "Payment Method",
    "Location",
    "Transaction Date"
}

class DataQualityError(Exception):
    pass
    
def check_raw(df):
    
    if df.empty:
        raise DataQualityError("O dataframe está vazio")
    
    missing_columns = EXPECTED_COLUMNS - set(df.columns)
    
    if missing_columns:
        raise DataQualityError(f"Colunas faltando: {sorted(missing_columns)}")