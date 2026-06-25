from fastapi.testclient import TestClient

from app.api.routes import get_agent_graph
from app.clients.llm_client import LLMClient
from app.core.config import get_settings
from app.graph.nodes import legal_rag as legal_rag_module
from app.graph.nodes import price_analysis as price_analysis_module
from app.graph.nodes import safety_analysis as safety_analysis_module
from app.main import app


client = TestClient(app)


def internal_api_headers() -> dict[str, str]:
    return {"X-Internal-Api-Key": get_settings().internal_api_key}


def route_as(monkeypatch, *workers: str) -> None:
    """Mock supervisor routing so workers are called in the given order."""
    call_count = {"n": 0}
    worker_list = list(workers)

    def fake_decide(self, message, workers_called):
        idx = call_count["n"]
        call_count["n"] += 1
        if idx < len(worker_list):
            return worker_list[idx]
        return "FINISH"

    monkeypatch.setattr(LLMClient, "decide_next_worker", fake_decide)
    get_agent_graph.cache_clear()


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


def test_agent_chat_returns_workers_called_and_answer(monkeypatch) -> None:
    route_as(monkeypatch, "PROPERTY_SEARCH")

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
    assert body["workersCalled"] == ["PROPERTY_SEARCH"]
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
    route_as(monkeypatch, "LEGAL_CONSULT")

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
    assert body["workersCalled"] == ["LEGAL_CONSULT"]
    assert body["answer"]
    assert len(body["legalCards"]) >= 1
    card = body["legalCards"][0]
    assert card_text_in_answer(body["answer"], card)
    assert card["lawName"] == "주택임대차보호법"
    assert card["articleNo"]
    assert card["title"]
    assert card["content"]
    assert isinstance(card["score"], (int, float))


def test_agent_chat_returns_price_analysis_card_for_selected_property(monkeypatch) -> None:
    class FakeSpringClient:
        def analyze_price(self, message: str, context: dict) -> dict:
            return {
                "selectedPropertyId": context["selectedPropertyId"],
                "summary": "최근 거래와 지역 통계를 확인했습니다.",
                "metrics": {
                    "comparableTransactionCount": 2,
                    "regionStatCount": 1,
                    "buildingStatCount": 1,
                },
                "transactions": [
                    {
                        "contractYearMonth": "2026-05",
                        "deposit": 10000000,
                        "monthlyRent": 520000,
                        "areaM2": 21.8,
                    }
                ],
                "priceAnalysis": {
                    "regionStats": [
                        {
                            "avgDeposit": 10500000,
                            "avgMonthlyRent": 520000,
                            "transactionCount": 3,
                        }
                    ],
                    "buildingStats": [],
                },
                "stub": False,
            }

    monkeypatch.setattr(price_analysis_module, "SpringClient", FakeSpringClient)
    route_as(monkeypatch, "PRICE_ANALYSIS")

    response = client.post(
        "/internal/agent/chat",
        headers=internal_api_headers(),
        json={
            "userId": "user-1",
            "sessionId": None,
            "message": "이 매물 가격이 비싼 편이야?",
            "context": {"selectedPropertyId": "1", "recentMessages": []},
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["workersCalled"] == ["PRICE_ANALYSIS"]
    assert body["analysisCards"]
    card = body["analysisCards"][0]
    assert card["type"] == "PRICE"
    assert card["title"]
    assert card["summary"]
    assert card["metrics"]["selectedPropertyId"] == "1"
    assert card["metrics"]["comparableTransactionCount"] == 2
    assert card["metrics"]["stub"] is False
    assert "최근 거래 2건" in body["answer"]
    assert "지역 평균 보증금 10,500,000원" in body["answer"]


def test_agent_chat_returns_price_analysis_error_metric_on_fallback(monkeypatch) -> None:
    class FakeSpringClient:
        def analyze_price(self, message: str, context: dict) -> dict:
            return {
                "selectedPropertyId": context["selectedPropertyId"],
                "summary": "시세 데이터를 불러오지 못했습니다.",
                "error": "SPRING_API_UNAVAILABLE",
                "metrics": {},
                "stub": False,
            }

    monkeypatch.setattr(price_analysis_module, "SpringClient", FakeSpringClient)
    route_as(monkeypatch, "PRICE_ANALYSIS")

    response = client.post(
        "/internal/agent/chat",
        headers=internal_api_headers(),
        json={
            "userId": "user-1",
            "sessionId": None,
            "message": "이 매물 가격 분석해줘",
            "context": {"selectedPropertyId": "1", "recentMessages": []},
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["workersCalled"] == ["PRICE_ANALYSIS"]
    card = body["analysisCards"][0]
    assert card["metrics"]["error"] == "SPRING_API_UNAVAILABLE"
    assert card["metrics"]["stub"] is False


def test_agent_chat_returns_safety_analysis_card_for_selected_property(monkeypatch) -> None:
    class FakeSpringClient:
        def analyze_safety(self, message: str, context: dict) -> dict:
            return {
                "selectedPropertyId": context["selectedPropertyId"],
                "summary": "반경 500m 기준 안전 점수는 78점입니다.",
                "score": 78,
                "metrics": {
                    "radius": 500,
                    "cctvCount300m": 8,
                    "bellCount300m": 2,
                    "lightCount300m": 14,
                    "policeCount500m": 1,
                },
                "safetySummary": {
                    "radius": 500,
                    "safetyScore": 78,
                    "cctvCount300m": 8,
                    "bellCount300m": 2,
                    "lightCount300m": 14,
                    "policeCount500m": 1,
                },
                "stub": False,
            }

    monkeypatch.setattr(safety_analysis_module, "SpringClient", FakeSpringClient)
    route_as(monkeypatch, "SAFETY_ANALYSIS")

    response = client.post(
        "/internal/agent/chat",
        headers=internal_api_headers(),
        json={
            "userId": "user-1",
            "sessionId": None,
            "message": "주변 cctv는 괜찮아?",
            "context": {"selectedPropertyId": "1", "recentMessages": []},
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["workersCalled"] == ["SAFETY_ANALYSIS"]
    assert body["analysisCards"]
    card = body["analysisCards"][0]
    assert card["type"] == "SAFETY"
    assert card["title"] == "안전 분석"
    assert card["summary"] == "반경 500m 기준 안전 점수는 78점입니다."
    assert card["metrics"]["selectedPropertyId"] == "1"
    assert card["score"] == 78
    assert card["metrics"]["radius"] == 500
    assert card["metrics"]["stub"] is False
    assert "안전 점수 78점" in body["answer"]
    assert "CCTV 8개" in body["answer"]


def card_text_in_answer(answer: str, card: dict) -> bool:
    return card["lawName"] in answer and card["articleNo"] in answer
