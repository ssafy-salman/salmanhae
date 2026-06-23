from app.clients.spring_client import SpringClient
from app.graph.state import AgentState


def safety_analysis(state: AgentState) -> AgentState:
    client = SpringClient()
    result = client.analyze_safety(
        message=state["message"],
        context=state.get("context", {}),
    )
    analysis_card = {
        "type": "SAFETY",
        "title": "안전 분석",
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
            "safetyAnalysis": result,
        },
    }
