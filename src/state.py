from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: List[BaseMessage]
    user_question: str
    current_datetime_str: str

    query_plan: Optional[Dict[str, Any]]

    query_result: Optional[List[Dict[str, Any]]]
    query_result_summary: Optional[str]

    error: Optional[str]
    final_answer: Optional[str]