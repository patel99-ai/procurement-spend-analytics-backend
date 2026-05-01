"""
Procurement Spend Data Ingestion Module
Loads and performs initial validation of raw procurement CSV data.
"""

import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "raw", "procurement_spend_raw.csv"
)

EXPECTED_COLUMNS = [
    "po_id", "po_date", "supplier_id", "supplier_name", "category",
    "subcategory", "department", "country", "amount_usd", "currency",
    "payment_terms", "status", "invoice_id", "invoice_date",
    "quantity", "unit_price",
]

NUMERIC_COLUMNS = ["amount_usd", "quantity", "unit_price"]
DATE_COLUMNS = ["po_date", "invoice_date"]


def load_raw_data(path: str = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw procurement CSV into a DataFrame."""
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")

    df = pd.read_csv(path, dtype=str)  # Load all as str first to preserve raw values
    logger.info("Loaded %d rows and %d columns from %s", len(df), len(df.columns), path)
    return df


def validate_columns(df: pd.DataFrame) -> None:
    """Raise ValueError if any expected columns are missing."""
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")
    logger.info("Column validation passed.")


def cast_types(df: pd.DataFrame) -> pd.DataFrame:
    """Cast columns to appropriate types; invalid values become NaN."""
    df = df.copy()

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col].str.strip(), errors="coerce")

    for col in DATE_COLUMNS:
        df[col] = pd.to_datetime(df[col].str.strip(), errors="coerce")

    # Strip whitespace from string columns
    str_cols = [c for c in df.columns if c not in NUMERIC_COLUMNS + DATE_COLUMNS]
    for col in str_cols:
        df[col] = df[col].str.strip().replace("", pd.NA)

    logger.info("Type casting complete.")
    return df


def flag_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Add boolean flag columns for common data quality issues."""
    df = df.copy()
    df["flag_missing_amount"] = df["amount_usd"].isna()
    df["flag_missing_supplier"] = df["supplier_id"].isna() | df["supplier_name"].isna()
    df["flag_zero_quantity"] = df["quantity"].notna() & (df["quantity"] == 0)
    df["flag_cancelled"] = df["status"].str.lower().eq("cancelled")
    df["flag_pending_no_invoice"] = (
        df["status"].str.lower().eq("pending") & df["invoice_id"].isna()
    )
    anomaly_count = df[
        ["flag_missing_amount", "flag_missing_supplier", "flag_zero_quantity",
         "flag_cancelled", "flag_pending_no_invoice"]
    ].sum()
    logger.info("Anomaly flags:\n%s", anomaly_count.to_string())
    return df


def load_and_prepare(path: str = RAW_DATA_PATH) -> pd.DataFrame:
    """
    Full ingestion pipeline:
      1. Load CSV
      2. Validate columns
      3. Cast types
      4. Flag anomalies
    Returns a clean, typed DataFrame ready for analysis.
    """
    df = load_raw_data(path)
    validate_columns(df)
    df = cast_types(df)
    df = flag_anomalies(df)
    logger.info("Ingestion complete. Final shape: %s", df.shape)
    return df


if __name__ == "__main__":
    df = load_and_prepare()
    print(df.dtypes)
    print(df.head())
