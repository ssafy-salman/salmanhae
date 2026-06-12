from functools import lru_cache

from fastapi import APIRouter, Depends

from app.api.schemas import AgentChatRequest, AgentChatResponse
from app.core.security import verify_internal_api_key
from app.graph.builder import build_agent_graph

router = APIRouter()


@lru_cache
def get_agent_graph():
    return build_agent_graph()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "backend-ai"}


@router.post(
    "/internal/agent/chat",
    response_model=AgentChatResponse,
    response_model_by_alias=True,
    dependencies=[Depends(verify_internal_api_key)],
)
def agent_chat(request: AgentChatRequest) -> AgentChatResponse:
    state = {
        "user_id": request.user_id,
        "session_id": request.session_id,
        "message": request.message,
        "context": request.context.model_dump(by_alias=True),
        "properties": [],
        "legal_cards": [],
        "tool_results": {},
        "next_actions": [],
    }
    result = get_agent_graph().invoke(state)
    return AgentChatResponse(
        intent=result["intent"],
        answer=result["answer"],
        properties=result.get("properties", []),
        legalCards=result.get("legal_cards", []),
        toolResults=result.get("tool_results", {}),
        nextActions=result.get("next_actions", []),
    )
