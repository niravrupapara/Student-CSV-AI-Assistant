import datetime
from langgraph.graph import StateGraph, END

from src.state import AgentState
from src.query_planner import planner_node
from src.query_executor import executor_node
from src.validator import validator_node, route_after_validation
from src.answer_generator import answer_node

def build_student_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("answer_generator", answer_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", "validator")
    workflow.add_conditional_edges("validator", route_after_validation, {
        "planner": "planner",
        "answer_generator": "answer_generator"
    })
    workflow.add_edge("answer_generator", END)

    return workflow.compile()

def run_agent_query(graph, user_question: str, message_history: list) -> str:
    initial_state = {
        "user_question": user_question,
        "messages": list(message_history),
        "current_datetime_str": datetime.datetime.now().strftime("%A, %Y-%m-%d %H:%M"),
        "retry_count": 0
    }
    final_state = graph.invoke(initial_state)
    return final_state.get("final_answer", "No answer found.")
