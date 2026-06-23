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


LEGAL_KEYWORDS = [
    "법",
    "계약",
    "임대차",
    "대항력",
    "확정일자",
    "보증금 반환",
    "전세사기",
    "묵시적 갱신",
]
PRICE_KEYWORDS = ["시세", "실거래", "가격", "비싼", "싼", "평균가", "전고점"]
SAFETY_KEYWORDS = ["안전", "치안", "cctv", "비상벨", "보안등", "파출소", "범죄"]
HUG_KEYWORDS = ["hug", "보증보험", "보증 가능", "보증 가입", "보증금 보험"]
PROPERTY_KEYWORDS = ["추천", "찾아", "매물", "원룸", "오피스텔", "아파트", "월세", "전세", "관악구"]


def classify_intent_fallback(message: str) -> Intent:
    normalized = message.lower()
    if any(keyword in normalized for keyword in LEGAL_KEYWORDS):
        return Intent.LEGAL_CONSULT
    if any(keyword in normalized for keyword in HUG_KEYWORDS):
        return Intent.HUG_CALC
    if any(keyword in normalized for keyword in PRICE_KEYWORDS):
        return Intent.PRICE_ANALYSIS
    if any(keyword in normalized for keyword in SAFETY_KEYWORDS):
        return Intent.SAFETY_ANALYSIS
    if any(keyword in normalized for keyword in PROPERTY_KEYWORDS):
        return Intent.PROPERTY_SEARCH
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
