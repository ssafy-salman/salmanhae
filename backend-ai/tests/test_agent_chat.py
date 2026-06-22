from fastapi.testclient import TestClient

from app.api.routes import get_agent_graph
from app.core.config import get_settings
from app.graph.nodes import legal_rag as legal_rag_module
from app.graph.nodes.classify_intent import classify_message
from app.graph.state import Intent
from app.main import app


client = TestClient(app)


def internal_api_headers() -> dict[str, str]:
    return {"X-Internal-Api-Key": get_settings().internal_api_key}


def test_agent_chat_requires_internal_api_key() -> None:
    response = client.post(
        "/internal/agent/chat",
        json={
            "userId": "user-1",
            "sessionId": None,
            "message": "관악구 보증금 5천 이하 원룸 추천해줘",
            "context": {"selectedPropertyId": None, "recentMessages": []},
        },
    )

    assert response.status_code == 401


def test_agent_chat_returns_intent_and_answer() -> None:
    response = client.post(
        "/internal/agent/chat",
        headers=internal_api_headers(),
        json={
            "userId": "user-1",
            "sessionId": None,
            "message": "관악구 보증금 5천 이하 원룸 추천해줘",
            "context": {"selectedPropertyId": None, "recentMessages": []},
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["intent"] == "PROPERTY_SEARCH"
    assert body["answer"]
    assert "properties" in body


def test_agent_chat_returns_legal_cards_for_legal_question(monkeypatch) -> None:
    class FakeRetriever:
        def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
            return [
                {
                    "lawName": "주택임대차보호법",
                    "articleNo": "제3조의2",
                    "title": "보증금의 회수",
                    "content": "임차인은 보증금을 우선변제받을 권리가 있다.",
                    "score": 0.86,
                }
            ]

    monkeypatch.setattr(legal_rag_module, "LegalRetriever", FakeRetriever)
    get_agent_graph.cache_clear()

    response = client.post(
        "/internal/agent/chat",
        headers=internal_api_headers(),
        json={
            "userId": "user-1",
            "sessionId": None,
            "message": "계약 전 보증금 반환 관련 법을 알려줘",
            "context": {"selectedPropertyId": None, "recentMessages": []},
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["intent"] == "LEGAL_CONSULT"
    assert body["answer"]
    assert len(body["legalCards"]) >= 1
    card = body["legalCards"][0]
    assert card["lawName"] == "주택임대차보호법"
    assert card["articleNo"]
    assert card["title"]
    assert card["content"]
    assert isinstance(card["score"], (int, float))


def test_classify_intent_examples() -> None:
    assert classify_message("관악구 보증금 5천 이하 원룸 추천해줘") == Intent.PROPERTY_SEARCH
    assert classify_message("계약 전에 법을 확인하고 싶어") == Intent.LEGAL_CONSULT
    assert classify_message("이 매물 가격이 비싼 편이야?") == Intent.PRICE_ANALYSIS
    assert classify_message("주변 cctv는 괜찮아?") == Intent.SAFETY_ANALYSIS
    assert classify_message("hug 보증보험 가능해?") == Intent.HUG_CALC
