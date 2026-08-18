import json
import streamlit as st
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.state import AgentState
from src.prompts import PLANNER_SYSTEM_PROMPT
from src.data_loader import extract_schema_info
from src.llm_client import get_llm_client
from src.logger import logger

class QueryPlan(BaseModel):
    operation: str = Field(default="filter")
    filters: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    columns: Optional[List[str]] = Field(default_factory=list)
    sort_by: Optional[str] = Field(default=None)
    ascending: bool = Field(default=True)
    limit: Optional[int] = Field(default=None)
    last_only: bool = Field(default=False)
    target_column: Optional[str] = Field(default=None)
    explanation: Optional[str] = Field(default=None)

    @field_validator("columns", "filters", mode="before")
    def handle_null_lists(cls, v):
        return v if v is not None else []

def planner_node(state: AgentState) -> Dict[str, Any]:
    user_question = state.get("user_question", "")
    df = st.session_state.get("dataframe")
    schema_info = extract_schema_info(df) if df is not None else {}
    current_dt = state.get("current_datetime_str", "")

    logger.info(f"question: {user_question}")

    system_prompt = PLANNER_SYSTEM_PROMPT.format(
        current_datetime_str=current_dt,
        total_rows=schema_info.get("total_rows", 0),
        columns=schema_info.get("columns", []),
        column_types=schema_info.get("column_types", {}),
        distinct_values=json.dumps(schema_info.get("distinct_values", {}), indent=2),
        sample_rows=json.dumps(schema_info.get("sample_rows", []), indent=2)
    )

    messages = [SystemMessage(content=system_prompt)]

    for msg in state.get("messages", [])[-4:]:
        if isinstance(msg, (HumanMessage, AIMessage)):
            messages.append(msg)

    messages.append(HumanMessage(content=user_question))

    llm = get_llm_client()
    response = llm.invoke(messages)
    content = response.content.strip()

    if content.startswith("```json"): content = content[7:]
    if content.startswith("```"): content = content[3:]
    if content.endswith("```"): content = content[:-3]

    raw_json = json.loads(content.strip())
    plan_dict = QueryPlan(**raw_json).model_dump()

    logger.info(f"query_plan: {json.dumps(plan_dict)}")
    return {"query_plan": plan_dict, "error": None}
