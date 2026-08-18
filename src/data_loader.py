import pandas as pd
import streamlit as st
from typing import Dict, Any
from src.logger import logger

def load_csv_data(source: Any) -> pd.DataFrame:
    df = pd.read_csv(source)
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.select_dtypes(include=['object', 'string']).columns:
        df[col] = df[col].astype(str).str.strip()
    logger.info(f"CSV Loaded: {len(df)} rows, {len(df.columns)} columns.")
    return df

@st.cache_data
def extract_schema_info(_df: pd.DataFrame) -> Dict[str, Any]:
    distincts = {
        col: _df[col].dropna().unique().tolist()[:15]
        for col in _df.columns
        if _df[col].dtype == 'object' or _df[col].nunique() <= 30
    }
    return {
        "columns": list(_df.columns),
        "column_types": {c: str(_df[c].dtype) for c in _df.columns},
        "total_rows": len(_df),
        "distinct_values": distincts,
        "sample_rows": _df.head(3).to_dict(orient='records')
    }
