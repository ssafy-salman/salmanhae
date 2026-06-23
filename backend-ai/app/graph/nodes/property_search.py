from app.clients.llm_client import LLMClient
from app.clients.supabase_client import SupabaseVectorClient
from app.graph.state import AgentState


def property_search(state: AgentState) -> AgentState:
    message = state["message"]
    criteria = LLMClient().extract_property_criteria(message)
    try:
        properties = SupabaseVectorClient().search_properties(criteria)
        property_search_meta = {"count": len(properties), "criteria": criteria}
    except Exception as exc:
        properties = []
        property_search_meta = {
            "count": 0,
            "criteria": criteria,
            "error": "PROPERTY_SEARCH_UNAVAILABLE",
            "errorDetail": str(exc),
        }
    return {
        **state,
        "properties": properties,
        "tool_results": {
            **state.get("tool_results", {}),
            "propertySearch": property_search_meta,
        },
    }
