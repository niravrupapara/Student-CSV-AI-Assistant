from typing import Dict, Any
from src.state import AgentState

MAX_RETRIES = 3

def validator_node(state: AgentState) -> Dict[str, Any]:
    if state.get("error") or not state.get("query_plan"):
        return {"is_valid": False, "retry_count": state.get("retry_count", 0) + 1}
    return {"is_valid": True}

def route_after_validation(state: AgentState) -> str:
    if state.get("is_valid") or state.get("retry_count", 0) >= MAX_RETRIES:
        return "answer_generator"
    return "planner"
