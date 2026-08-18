import pandas as pd
import streamlit as st
from typing import Dict, Any, List, Tuple
from src.state import AgentState
from src.data_loader import load_csv_data
from src.logger import logger

def execute_pandas_query(df: pd.DataFrame, plan: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str, int]:
    if df is None or df.empty:
        return [], "DataFrame is empty.", 0

    filtered_df = df.copy()
    operation = plan.get("operation", "filter")
    filters = plan.get("filters", [])
    columns = plan.get("columns", [])
    sort_by = plan.get("sort_by")
    ascending = plan.get("ascending", True)
    limit = plan.get("limit")
    last_only = plan.get("last_only", False)
    target_column = plan.get("target_column")

    # Apply Filters
    for cond in filters:
        col = cond.get("column")
        op = cond.get("operator", "eq")
        val = cond.get("value")

        if not col or col not in filtered_df.columns or val is None or val == "":
            continue

        val_str = str(val).strip()

        if op == "eq":
            if filtered_df[col].dtype == "object":
                filtered_df = filtered_df[filtered_df[col].astype(str).str.lower() == val_str.lower()]
            else:
                filtered_df = filtered_df[filtered_df[col] == val]
        elif op == "ne":
            if filtered_df[col].dtype == "object":
                filtered_df = filtered_df[filtered_df[col].astype(str).str.lower() != val_str.lower()]
            else:
                filtered_df = filtered_df[filtered_df[col] != val]
        elif op == "contains":
            filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(val_str, case=False, na=False, regex=False)]
        elif op in ["gt", "gte", "lt", "lte"]:
            if pd.api.types.is_numeric_dtype(filtered_df[col]):
                num_val = float(val)
                if op == "gt": filtered_df = filtered_df[filtered_df[col] > num_val]
                elif op == "gte": filtered_df = filtered_df[filtered_df[col] >= num_val]
                elif op == "lt": filtered_df = filtered_df[filtered_df[col] < num_val]
                elif op == "lte": filtered_df = filtered_df[filtered_df[col] <= num_val]
            else:
                col_str = filtered_df[col].astype(str)
                if op == "gt": filtered_df = filtered_df[col_str > val_str]
                elif op == "gte": filtered_df = filtered_df[col_str >= val_str]
                elif op == "lt": filtered_df = filtered_df[col_str < val_str]
                elif op == "lte": filtered_df = filtered_df[col_str <= val_str]
        elif op == "in" and isinstance(val, list):
            val_list = [str(v).lower() for v in val]
            filtered_df = filtered_df[filtered_df[col].astype(str).str.lower().isin(val_list)]

    total_matches = len(filtered_df)

    if sort_by and sort_by in filtered_df.columns:
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)

    if last_only:
        filtered_df = filtered_df.tail(1)
    elif limit and limit > 0:
        filtered_df = filtered_df.head(limit)

    if operation == "count":
        return [{"count": total_matches}], f"Total count: {total_matches}", total_matches

    if operation == "unique" and target_column and target_column in df.columns:
        uniques = filtered_df[target_column].dropna().unique().tolist()
        summary = f"Unique values in '{target_column}': {', '.join(map(str, uniques))}"
        records = [{target_column: u} for u in uniques]
        return records, summary, len(uniques)

    valid_cols = [c for c in columns if c in filtered_df.columns] or list(filtered_df.columns)
    result_df = filtered_df[valid_cols]
    records = result_df.to_dict(orient="records")
    summary = "No matching records found." if total_matches == 0 else result_df.to_string(index=False)

    return records, summary, total_matches

def executor_node(state: AgentState) -> Dict[str, Any]:
    plan = state.get("query_plan")
    if not plan:
        return {"query_result": [], "query_result_summary": "No query plan.", "error": "Missing plan."}
    try:
        df = st.session_state.get("dataframe")
        if df is None:
            return {"query_result": [], "query_result_summary": "No CSV data loaded.", "error": "DataFrame not loaded."}
            
        records, summary, total_matches = execute_pandas_query(df, plan)
        logger.info(f"pandas_result: {summary}")
        return {"query_result": records, "query_result_summary": summary, "error": None}
    except Exception as e:
        return {"query_result": [], "query_result_summary": "Execution error.", "error": str(e)}
