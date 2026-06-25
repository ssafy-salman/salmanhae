from app.clients.llm_client import LLMClient
from app.clients.supabase_client import SupabaseVectorClient
from app.graph.state import AgentState


_DEFAULT_LIMIT = 10
_SORTED_LIMIT = 5


def property_search(state: AgentState) -> AgentState:
    message = state["message"]
    criteria = LLMClient().extract_property_criteria(message)

    user_limit = criteria.get("limit")
    try:
        effective_limit = int(user_limit) if user_limit else (
            _SORTED_LIMIT if criteria.get("sort_by") else _DEFAULT_LIMIT
        )
    except (TypeError, ValueError):
        effective_limit = _DEFAULT_LIMIT

    try:
        properties = SupabaseVectorClient().search_properties(criteria, limit=effective_limit)
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
