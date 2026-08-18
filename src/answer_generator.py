from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.state import AgentState
from src.prompts import ANSWER_GENERATOR_PROMPT
from src.llm_client import get_llm_client
from src.logger import logger

def answer_node(state: AgentState) -> Dict[str, Any]:
    user_question = state.get("user_question", "")
    query_plan = state.get("query_plan", {})
    query_result = state.get("query_result", [])
    query_result_summary = state.get("query_result_summary", "No results.")
    
    explanation = query_plan.get("explanation", "Query executed") if query_plan else "Query executed"
    total_matches = len(query_result) if isinstance(query_result, list) else 0

    system_prompt = ANSWER_GENERATOR_PROMPT.format(
        user_question=user_question,
        query_explanation=explanation,
        query_result_summary=query_result_summary,
        total_matches=total_matches
    )

    llm = get_llm_client()
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_question)
    ])
    final_answer = response.content.strip()
    logger.info(f"final_answer: {final_answer}")

    return {
        "final_answer": final_answer,
        "messages": state.get("messages", []) + [AIMessage(content=final_answer)]
    }
