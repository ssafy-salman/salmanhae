from app.clients.spring_client import SpringClient
from app.graph.state import AgentState


def property_search(state: AgentState) -> AgentState:
    client = SpringClient()
    result = client.search_properties(
        message=state["message"],
        context=state.get("context", {}),
    )
    return {
        **state,
        "properties": result["properties"],
        "tool_results": {
            **state.get("tool_results", {}),
            "propertySearch": result["meta"],
        },
    }
