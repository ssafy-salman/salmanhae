from typing import Literal

from pydantic import BaseModel, ValidationError

from app.clients.llm_client import LLMClient
from app.graph.state import AgentState, Intent


class RouteDecision(BaseModel):
    intent: Literal[
        "PROPERTY_SEARCH",
        "LEGAL_CONSULT",
        "PRICE_ANALYSIS",
        "SAFETY_ANALYSIS",
        "HUG_CALC",
        "GENERAL_CHAT",
    ]
    reasoning: str


def classify_intent_fallback(message: str) -> Intent:
    return Intent.FALLBACK


def classify_intent_llm(message: str) -> Intent:
    raw = LLMClient().classify(message)
    if raw is None:
        return classify_intent_fallback(message)
    try:
        decision = RouteDecision.model_validate(raw)
        return Intent(decision.intent)
    except (ValueError, ValidationError):
        return classify_intent_fallback(message)


def classify_intent(state: AgentState) -> AgentState:
    return {**state, "intent": classify_intent_llm(state["message"])}
