from app.clients.spring_client import SpringClient
from app.graph.state import AgentState


def price_analysis(state: AgentState) -> AgentState:
    client = SpringClient()
    result = client.analyze_price(
        message=state["message"],
        context=state.get("context", {}),
    )
    analysis_card = {
        "type": "PRICE",
        "title": "시세 분석",
        "summary": result["summary"],
        "score": result.get("score"),
        "metrics": {
            "selectedPropertyId": result.get("selectedPropertyId"),
            "stub": result.get("stub", False),
        },
    }
    return {
        **state,
        "analysis_cards": [*state.get("analysis_cards", []), analysis_card],
        "tool_results": {
            **state.get("tool_results", {}),
            "priceAnalysis": result,
        },
    }
