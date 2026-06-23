from app.clients.llm_client import LLMClient
from app.clients.supabase_client import SupabaseVectorClient
from app.graph.state import AgentState


def property_search(state: AgentState) -> AgentState:
    criteria = LLMClient().extract_property_criteria(state["message"])
    properties = SupabaseVectorClient().search_properties(criteria)
    return {
        **state,
        "properties": properties,
        "tool_results": {
            **state.get("tool_results", {}),
            "propertySearch": {"count": len(properties), "criteria": criteria},
        },
    }
