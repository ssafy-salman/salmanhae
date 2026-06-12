from langgraph.graph import END, START, StateGraph

from app.graph.nodes.classify_intent import classify_intent
from app.graph.nodes.generate_answer import generate_answer
from app.graph.nodes.legal_rag import legal_rag
from app.graph.nodes.price_analysis import price_analysis
from app.graph.nodes.property_search import property_search
from app.graph.nodes.safety_analysis import safety_analysis
from app.graph.state import AgentState, Intent


def route_by_intent(state: AgentState) -> str:
    intent = state.get("intent", Intent.FALLBACK)
    return {
        Intent.PROPERTY_SEARCH: "property_search",
        Intent.LEGAL_CONSULT: "legal_rag",
        Intent.PRICE_ANALYSIS: "price_analysis",
        Intent.SAFETY_ANALYSIS: "safety_analysis",
        Intent.HUG_CALC: "fallback",
        Intent.FALLBACK: "fallback",
    }[intent]


def fallback(state: AgentState) -> AgentState:
    next_actions = state.get("next_actions", [])
    next_actions.append(
        {
            "type": "ASK_CLARIFYING_QUESTION",
            "label": "질문 구체화",
        }
    )
    return {
        **state,
        "tool_results": {
            **state.get("tool_results", {}),
            "fallback": {"reason": "No MVP tool is available for this intent yet."},
        },
        "next_actions": next_actions,
    }


def build_agent_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("property_search", property_search)
    workflow.add_node("legal_rag", legal_rag)
    workflow.add_node("price_analysis", price_analysis)
    workflow.add_node("safety_analysis", safety_analysis)
    workflow.add_node("fallback", fallback)
    workflow.add_node("generate_answer", generate_answer)

    workflow.add_edge(START, "classify_intent")
    workflow.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "property_search": "property_search",
            "legal_rag": "legal_rag",
            "price_analysis": "price_analysis",
            "safety_analysis": "safety_analysis",
            "fallback": "fallback",
        },
    )

    for node_name in ["property_search", "legal_rag", "price_analysis", "safety_analysis", "fallback"]:
        workflow.add_edge(node_name, "generate_answer")

    workflow.add_edge("generate_answer", END)
    return workflow.compile()
