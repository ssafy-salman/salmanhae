from collections.abc import Callable
from typing import Any

import httpx

from app.core.config import get_settings


HttpGet = Callable[..., httpx.Response]


class SpringClient:
    """Client boundary for Spring Boot domain APIs."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
        http_get: HttpGet = httpx.get,
    ) -> None:
        settings = get_settings()
        configured_base_url = base_url if base_url is not None else settings.spring_api_base_url
        self.base_url = configured_base_url.rstrip("/")
        self.timeout_seconds = (
            timeout_seconds if timeout_seconds is not None else settings.spring_api_timeout_seconds
        )
        self.http_get = http_get

    def search_properties(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "properties": [],
            "meta": {"baseUrl": self.base_url, "query": message, "stub": True},
        }

    def analyze_price(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        selected_property_id = self._selected_property_id(context)
        if selected_property_id is None:
            return self._selection_required_payload(message)

        try:
            property_detail = self._get(f"/api/v1/properties/{selected_property_id}")
            transactions = self._get(
                f"/api/v1/properties/{selected_property_id}/transactions",
                params={"years": 3},
            )
            price_analysis = self._get(
                "/api/v1/price-analysis",
                params={
                    "legalDongCode": property_detail["legalDongCode"],
                    "propertyType": property_detail["propertyType"],
                    "transactionType": property_detail["transactionType"],
                },
            )
            if not isinstance(property_detail, dict) or not isinstance(price_analysis, dict):
                raise ValueError("Spring analysis payload must be an object")
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            return self._fallback_payload(
                message=message,
                selected_property_id=selected_property_id,
                error=str(exc),
                summary="선택한 매물의 시세 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.",
            )

        transaction_items = self._items(transactions)
        region_stats = self._items(price_analysis.get("regionStats", []))
        building_stats = self._items(price_analysis.get("buildingStats", []))
        building_name = property_detail.get("buildingName") or property_detail.get("title") or "선택 매물"

        return {
            "baseUrl": self.base_url,
            "query": message,
            "selectedPropertyId": selected_property_id,
            "summary": (
                f"{building_name} 기준으로 최근 거래 {len(transaction_items)}건과 "
                f"지역 통계 {len(region_stats)}건을 확인했습니다."
            ),
            "property": property_detail,
            "transactions": transaction_items,
            "priceAnalysis": price_analysis,
            "metrics": {
                "comparableTransactionCount": len(transaction_items),
                "regionStatCount": len(region_stats),
                "buildingStatCount": len(building_stats),
            },
            "stub": False,
        }

    def analyze_safety(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        selected_property_id = self._selected_property_id(context)
        if selected_property_id is None:
            return self._selection_required_payload(message)

        try:
            safety_summary = self._get(
                f"/api/v1/properties/{selected_property_id}/safety-summary",
                params={"radius": 500},
            )
            if not isinstance(safety_summary, dict):
                raise ValueError("Spring safety payload must be an object")
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            return self._fallback_payload(
                message=message,
                selected_property_id=selected_property_id,
                error=str(exc),
                summary="선택한 매물의 안전 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.",
            )

        safety_score = safety_summary.get("safetyScore")
        summary = "반경 500m 기준 안전 시설 정보를 확인했습니다."
        if safety_score is not None:
            summary = f"반경 500m 기준 안전 점수는 {safety_score}점입니다."

        return {
            "baseUrl": self.base_url,
            "query": message,
            "selectedPropertyId": selected_property_id,
            "summary": summary,
            "score": safety_score,
            "safetySummary": safety_summary,
            "metrics": {
                "radius": safety_summary.get("radius"),
                "cctvCount300m": safety_summary.get("cctvCount300m"),
                "bellCount300m": safety_summary.get("bellCount300m"),
                "lightCount300m": safety_summary.get("lightCount300m"),
                "policeCount500m": safety_summary.get("policeCount500m"),
            },
            "stub": False,
        }

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = self.http_get(
            f"{self.base_url}{path}",
            params=params,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or "data" not in payload:
            raise ValueError("Spring API response must contain data")
        return payload["data"]

    @staticmethod
    def _selected_property_id(context: dict[str, Any]) -> str | None:
        value = context.get("selectedPropertyId")
        if value is None:
            value = context.get("selected_property_id")
        if value is None:
            return None
        selected_property_id = str(value).strip()
        return selected_property_id or None

    @staticmethod
    def _items(value: Any) -> list[Any]:
        if isinstance(value, dict):
            items = value.get("items", [])
            return items if isinstance(items, list) else []
        return value if isinstance(value, list) else []

    def _selection_required_payload(self, message: str) -> dict[str, Any]:
        return {
            "baseUrl": self.base_url,
            "query": message,
            "selectedPropertyId": None,
            "summary": "분석할 매물을 먼저 선택해 주세요.",
            "requiresSelection": True,
            "metrics": {},
            "stub": False,
        }

    def _fallback_payload(
        self,
        message: str,
        selected_property_id: str,
        error: str,
        summary: str,
    ) -> dict[str, Any]:
        return {
            "baseUrl": self.base_url,
            "query": message,
            "selectedPropertyId": selected_property_id,
            "summary": summary,
            "error": "SPRING_API_UNAVAILABLE",
            "errorDetail": error,
            "metrics": {},
            "stub": False,
        }
