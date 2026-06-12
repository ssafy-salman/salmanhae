from enum import StrEnum
from typing import Any, NotRequired, TypedDict


class Intent(StrEnum):
    PROPERTY_SEARCH = "PROPERTY_SEARCH"
    LEGAL_CONSULT = "LEGAL_CONSULT"
    PRICE_ANALYSIS = "PRICE_ANALYSIS"
    SAFETY_ANALYSIS = "SAFETY_ANALYSIS"
    HUG_CALC = "HUG_CALC"
    FALLBACK = "FALLBACK"


class AgentState(TypedDict):
    user_id: str
    session_id: str | None
    message: str
    context: dict[str, Any]
    intent: NotRequired[Intent]
    answer: NotRequired[str]
    properties: NotRequired[list[dict[str, Any]]]
    legal_cards: NotRequired[list[dict[str, Any]]]
    tool_results: NotRequired[dict[str, Any]]
    next_actions: NotRequired[list[dict[str, Any]]]
