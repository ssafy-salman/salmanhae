import json
from unittest.mock import MagicMock

import pytest

from app.clients.llm_client import LLMClient
from app.graph.nodes.classify_intent import (
    RouteDecision,
    classify_intent_fallback,
    classify_intent_llm,
)
from app.graph.state import Intent


def _make_llm_response(intent: str, reasoning: str = "test") -> dict:
    """LLMClient.classify()가 반환할 dict를 만드는 헬퍼."""
    return {"intent": intent, "reasoning": reasoning}


# ---------------------------------------------------------------------------
# RouteDecision 스키마 검증
# ---------------------------------------------------------------------------

def test_route_decision_valid() -> None:
    decision = RouteDecision.model_validate(
        {"intent": "PROPERTY_SEARCH", "reasoning": "매물 검색 요청"}
    )
    assert decision.intent == "PROPERTY_SEARCH"


def test_route_decision_rejects_unknown_intent() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        RouteDecision.model_validate({"intent": "UNKNOWN", "reasoning": "?"})


# ---------------------------------------------------------------------------
# classify_intent_llm — LLM 응답 mock
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "message, llm_intent, expected",
    [
        (
            "강남구 오피스텔 가장 싼거 추천해줘",
            "PROPERTY_SEARCH",
            Intent.PROPERTY_SEARCH,
        ),
        (
            "강남구 오피스텔 시세 알려줘",
            "PRICE_ANALYSIS",
            Intent.PRICE_ANALYSIS,
        ),
        (
            "가성비 좋은 매물 추천해줘",
            "PROPERTY_SEARCH",
            Intent.PROPERTY_SEARCH,
        ),
        (
            "전세금 인상 관련 법 조항 알려줘",
            "LEGAL_CONSULT",
            Intent.LEGAL_CONSULT,
        ),
        (
            "안녕",
            "GENERAL_CHAT",
            Intent.GENERAL_CHAT,
        ),
    ],
)
def test_classify_intent_llm(monkeypatch, message, llm_intent, expected) -> None:
    monkeypatch.setattr(
        LLMClient,
        "classify",
        lambda self, msg: _make_llm_response(llm_intent),
    )
    assert classify_intent_llm(message) == expected


# ---------------------------------------------------------------------------
# classify_intent_llm — LLM 실패 시 fallback
# ---------------------------------------------------------------------------

def test_classify_intent_llm_falls_back_on_none(monkeypatch) -> None:
    monkeypatch.setattr(LLMClient, "classify", lambda self, msg: None)
    # "추천"이 PROPERTY_KEYWORDS에 있으므로 fallback도 PROPERTY_SEARCH 반환
    assert classify_intent_llm("관악구 원룸 추천해줘") == Intent.PROPERTY_SEARCH


def test_classify_intent_llm_falls_back_on_invalid_intent(monkeypatch) -> None:
    monkeypatch.setattr(
        LLMClient,
        "classify",
        lambda self, msg: {"intent": "TOTALLY_WRONG", "reasoning": "oops"},
    )
    # fallback 키워드 없는 메시지는 FALLBACK
    assert classify_intent_llm("그냥 아무 말") == Intent.FALLBACK


# ---------------------------------------------------------------------------
# classify_intent_fallback — 키워드 기반 (기존 로직 보존 확인)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "message, expected",
    [
        ("관악구 보증금 5천 이하 원룸 추천해줘", Intent.PROPERTY_SEARCH),
        ("계약 전에 법을 확인하고 싶어", Intent.LEGAL_CONSULT),
        ("이 매물 가격이 비싼 편이야?", Intent.PRICE_ANALYSIS),
        ("주변 cctv는 괜찮아?", Intent.SAFETY_ANALYSIS),
        ("hug 보증보험 가능해?", Intent.HUG_CALC),
        ("완전 뜬금없는 말", Intent.FALLBACK),
    ],
)
def test_classify_intent_fallback(message, expected) -> None:
    assert classify_intent_fallback(message) == expected
