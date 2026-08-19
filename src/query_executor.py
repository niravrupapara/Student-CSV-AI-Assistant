import pandas as pd
import streamlit as st

from src.state import AgentState
from src.logger import logger


def execute_query(df: pd.DataFrame, plan: dict):
    """Apply the planner filters and return matching records."""

    result = df.copy()

    # Apply filters
    for column, value in plan.get("filters", {}).items():

        if column not in result.columns:
            continue

        if value is None or value == "":
            continue

        # Case-insensitive matching for text columns
        if result[column].dtype == "object":
            result = result[
                result[column]
                .astype(str)
                .str.strip()
                .str.lower()
                == str(value).strip().lower()
            ]
        else:
            result = result[result[column] == value]

    # Return only requested columns
    columns = [
        column
        for column in plan.get("columns", [])
        if column in result.columns
    ]

    if columns:
        result = result[columns]

    return result.to_dict(orient="records")


def executor_node(state: AgentState):

    plan = state.get("query_plan")
    df = st.session_state.get("dataframe")

    if df is None:
        return {
            "query_result": [],
            "query_result_summary": "CSV data is not loaded.",
            "error": "DataFrame not loaded."
        }

    if not plan:
        return {
            "query_result": [],
            "query_result_summary": "No query plan.",
            "error": "Missing query plan."
        }

    try:
        records = execute_query(df, plan)

        summary = (
            "No matching records found."
            if not records
            else str(records)
        )

        logger.info(f"Query result: {records}")

        return {
            "query_result": records,
            "query_result_summary": summary,
            "error": None
        }

    except Exception as e:
        logger.error(f"Query execution error: {e}")

        return {
            "query_result": [],
            "query_result_summary": "Query execution failed.",
            "error": str(e)
        }