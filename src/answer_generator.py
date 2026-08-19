from typing import Dict, Any

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.state import AgentState
from src.prompts import ANSWER_GENERATOR_PROMPT
from src.llm_client import get_llm_client
from src.logger import logger


def answer_node(state: AgentState) -> Dict[str, Any]:

    question = state.get("user_question", "")
    result = state.get("query_result", [])
    summary = state.get("query_result_summary", "No results.")

    prompt = ANSWER_GENERATOR_PROMPT.format(
        user_question=question,
        query_result_summary=summary,
        total_matches=len(result)
    )

    try:
        llm = get_llm_client()

        response = llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=question)
        ])

        answer = response.content.strip()

        logger.info(f"Final answer: {answer}")

        return {
            "final_answer": answer,
            "messages": state.get("messages", []) + [
                AIMessage(content=answer)
            ]
        }

    except Exception as e:

        logger.error(f"Answer generation error: {e}")

        return {
            "final_answer": "Sorry, I could not generate an answer.",
            "error": str(e)
        }