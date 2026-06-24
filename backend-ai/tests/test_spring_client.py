from typing import Any

import httpx

from app.clients.spring_client import SpringClient


class FakeResponse:
    def __init__(self, data: Any) -> None:
        self.data = data

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return {"data": self.data, "message": "OK"}


def test_analyze_price_calls_spring_property_transactions_and_price_analysis() -> None:
    calls: list[tuple[str, dict[str, Any] | None, float]] = []

    def fake_get(url: str, params: dict[str, Any] | None = None, timeout: float = 0) -> FakeResponse:
        calls.append((url, params, timeout))
        if url.endswith("/api/v1/properties/7"):
            return FakeResponse(
                {
                    "id": 7,
                    "title": "Gwanak One Room",
                    "buildingName": "Green Villa",
                    "legalDongCode": "1162010200",
                    "propertyType": "ONE_ROOM",
                    "transactionType": "MONTHLY_RENT",
                }
            )
        if url.endswith("/api/v1/properties/7/transactions"):
            return FakeResponse({"items": [{"contractYearMonth": "2026-05"}], "totalCount": 1})
        if url.endswith("/api/v1/price-analysis"):
            return FakeResponse(
                {
                    "regionStats": [{"regionLevel": "DONG"}],
                    "buildingStats": [{"buildingKey": "building-1"}],
                }
            )
        raise AssertionError(f"unexpected URL: {url}")

    client = SpringClient(base_url="http://spring", timeout_seconds=2.5, http_get=fake_get)

    result = client.analyze_price("price?", {"selectedPropertyId": 7})

    assert result["selectedPropertyId"] == "7"
    assert result["stub"] is False
    assert result["summary"] == "Green Villa 기준으로 최근 거래 1건과 지역 통계 1건을 확인했습니다."
    assert result["metrics"]["comparableTransactionCount"] == 1
    assert result["metrics"]["regionStatCount"] == 1
    assert result["metrics"]["buildingStatCount"] == 1
    assert calls == [
        ("http://spring/api/v1/properties/7", None, 2.5),
        ("http://spring/api/v1/properties/7/transactions", {"years": 3}, 2.5),
        (
            "http://spring/api/v1/price-analysis",
            {
                "legalDongCode": "1162010200",
                "propertyType": "ONE_ROOM",
                "transactionType": "MONTHLY_RENT",
            },
            2.5,
        ),
    ]


def test_analyze_safety_calls_spring_safety_summary() -> None:
    calls: list[tuple[str, dict[str, Any] | None, float]] = []

    def fake_get(url: str, params: dict[str, Any] | None = None, timeout: float = 0) -> FakeResponse:
        calls.append((url, params, timeout))
        return FakeResponse(
            {
                "propertyId": 7,
                "radius": 500,
                "safetyScore": 78,
                "cctvCount300m": 8,
                "bellCount300m": 2,
                "lightCount300m": 14,
                "policeCount500m": 1,
            }
        )

    client = SpringClient(base_url="http://spring/", timeout_seconds=3, http_get=fake_get)

    result = client.analyze_safety("safe?", {"selectedPropertyId": "7"})

    assert result["selectedPropertyId"] == "7"
    assert result["score"] == 78
    assert result["summary"] == "반경 500m 기준 안전 점수는 78점입니다."
    assert result["safetySummary"]["safetyScore"] == 78
    assert result["metrics"]["radius"] == 500
    assert result["metrics"]["cctvCount300m"] == 8
    assert calls == [
        ("http://spring/api/v1/properties/7/safety-summary", {"radius": 500}, 3),
    ]


def test_analysis_requires_selected_property_without_http_call() -> None:
    calls: list[str] = []

    def fake_get(url: str, **kwargs: Any) -> FakeResponse:
        calls.append(url)
        return FakeResponse({})

    client = SpringClient(base_url="http://spring", http_get=fake_get)

    result = client.analyze_price("price?", {"selectedPropertyId": None})

    assert result["requiresSelection"] is True
    assert result["selectedPropertyId"] is None
    assert result["summary"] == "분석할 매물을 먼저 선택해 주세요."
    assert calls == []


def test_analysis_failure_returns_controlled_fallback() -> None:
    def fake_get(url: str, **kwargs: Any) -> FakeResponse:
        raise httpx.ConnectError("connection refused")

    client = SpringClient(base_url="http://spring", http_get=fake_get)

    result = client.analyze_safety("safe?", {"selectedPropertyId": "7"})

    assert result["selectedPropertyId"] == "7"
    assert result["error"] == "SPRING_API_UNAVAILABLE"
    assert result["stub"] is False
    assert result["summary"] == "선택한 매물의 안전 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요."
