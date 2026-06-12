from app.clients.spring_client import SpringClient
from app.graph.state import AgentState


def price_analysis(state: AgentState) -> AgentState:
    client = SpringClient()
    result = client.analyze_price(
        message=state["message"],
        context=state.get("context", {}),
    )
    return {
        **state,
        "tool_results": {
            **state.get("tool_results", {}),
            "priceAnalysis": result,
        },
    }
