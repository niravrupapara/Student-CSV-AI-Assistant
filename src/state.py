from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: List[BaseMessage]
    csv_schema_info: Dict[str, Any]
    user_question: str
    current_datetime_str: str
    query_plan: Optional[Dict[str, Any]]
    query_result: Optional[List[Dict[str, Any]]]
    query_result_summary: Optional[str]
    error: Optional[str]
    is_valid: bool
    retry_count: int
    final_answer: Optional[str]
