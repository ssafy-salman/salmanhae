from app.graph.state import AgentState
from app.rag.retriever import LegalRetriever


def legal_rag(state: AgentState) -> AgentState:
    retriever = LegalRetriever()
    cards = retriever.retrieve(state["message"])
    return {
        **state,
        "legal_cards": cards,
        "tool_results": {
            **state.get("tool_results", {}),
            "legalRag": {"topK": len(cards), "source": "supabase-pgvector-stub"},
        },
    }
