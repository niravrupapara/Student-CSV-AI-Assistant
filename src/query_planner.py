import json
import streamlit as st

from src.state import AgentState
from src.prompts import PLANNER_SYSTEM_PROMPT
from src.data_loader import extract_schema_info
from src.llm_client import get_llm_client
from src.logger import logger


def planner_node(state: AgentState):

    question = state.get("user_question", "")
    current_datetime = state.get("current_datetime_str", "")
    df = st.session_state.get("dataframe")

    if df is None:
        return {
            "query_plan": {},
            "error": "CSV data is not loaded."
        }

    try:
        # Get CSV schema information
        schema = extract_schema_info(df)

        # Build planner prompt
        prompt = PLANNER_SYSTEM_PROMPT.format(
            columns=schema.get("columns", []),
            column_types=schema.get("column_types", {}),
            sample_rows=schema.get("sample_rows", []),
            current_datetime_str=current_datetime,
            user_question=question,
        )

        # Ask LLM to create query plan
        llm = get_llm_client()
        response = llm.invoke(prompt)

        content = response.content.strip()

        # Remove Markdown code fences if the model adds them
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        plan = json.loads(content)

        # Keep only real CSV columns
        valid_columns = set(df.columns)

        plan["filters"] = {
            column: value
            for column, value in plan.get("filters", {}).items()
            if column in valid_columns
        }

        plan["columns"] = [
            column
            for column in plan.get("columns", [])
            if column in valid_columns
        ]

        logger.info(f"Question: {question}")
        logger.info(f"Query plan: {plan}")

        return {
            "query_plan": plan,
            "error": None
        }

    except Exception as e:
        logger.error(f"Planner error: {e}")

        return {
            "query_plan": {},
            "error": f"Failed to create query plan: {str(e)}"
        }