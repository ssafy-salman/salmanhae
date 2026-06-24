from typing import Any, NotRequired, TypedDict


class AgentState(TypedDict):
    user_id: str
    session_id: str | None
    message: str
    context: dict[str, Any]
    next_worker: NotRequired[str]
    workers_called: NotRequired[list[str]]
    answer: NotRequired[str]
    properties: NotRequired[list[dict[str, Any]]]
    legal_cards: NotRequired[list[dict[str, Any]]]
    analysis_cards: NotRequired[list[dict[str, Any]]]
    tool_results: NotRequired[dict[str, Any]]
    next_actions: NotRequired[list[dict[str, Any]]]
