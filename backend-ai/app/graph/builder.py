from langgraph.graph import END, START, StateGraph

from app.graph.nodes.general_chat import general_chat
from app.graph.nodes.generate_answer import generate_answer
from app.graph.nodes.legal_rag import legal_rag
from app.graph.nodes.price_analysis import price_analysis
from app.graph.nodes.property_search import property_search
from app.graph.nodes.safety_analysis import safety_analysis
from app.graph.nodes.supervisor import supervisor
from app.graph.state import AgentState


def route_after_supervisor(state: AgentState) -> str:
    mapping = {
        "PROPERTY_SEARCH": "property_search",
        "LEGAL_CONSULT": "legal_rag",
        "PRICE_ANALYSIS": "price_analysis",
        "SAFETY_ANALYSIS": "safety_analysis",
        "GENERAL_CHAT": "general_chat",
        "FINISH": "generate_answer",
    }
    return mapping.get(state.get("next_worker", "FINISH"), "generate_answer")


def build_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor)
    workflow.add_node("property_search", property_search)
    workflow.add_node("legal_rag", legal_rag)
    workflow.add_node("price_analysis", price_analysis)
    workflow.add_node("safety_analysis", safety_analysis)
    workflow.add_node("general_chat", general_chat)
    workflow.add_node("generate_answer", generate_answer)

    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "property_search": "property_search",
            "legal_rag": "legal_rag",
            "price_analysis": "price_analysis",
            "safety_analysis": "safety_analysis",
            "general_chat": "general_chat",
            "generate_answer": "generate_answer",
        },
    )

    for node in ["property_search", "legal_rag", "price_analysis", "safety_analysis", "general_chat"]:
        workflow.add_edge(node, "supervisor")

    workflow.add_edge("generate_answer", END)
    return workflow.compile()
