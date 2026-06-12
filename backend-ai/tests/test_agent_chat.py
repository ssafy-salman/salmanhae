from fastapi.testclient import TestClient

from app.graph.nodes.classify_intent import classify_message
from app.graph.state import Intent
from app.main import app


client = TestClient(app)


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
        headers={"X-Internal-Api-Key": "change-me"},
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


def test_classify_intent_examples() -> None:
    assert classify_message("관악구 보증금 5천 이하 원룸 추천해줘") == Intent.PROPERTY_SEARCH
    assert classify_message("전세사기 계약이면 어떻게 해야 해?") == Intent.LEGAL_CONSULT
    assert classify_message("이 매물 시세가 비싼 편이야?") == Intent.PRICE_ANALYSIS
    assert classify_message("주변 치안과 CCTV는 괜찮아?") == Intent.SAFETY_ANALYSIS
    assert classify_message("HUG 보증보험 가입 가능해?") == Intent.HUG_CALC
