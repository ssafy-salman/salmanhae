from typing import Any

from app.core.config import get_settings


class SpringClient:
    """Client boundary for Spring Boot domain APIs.

    The MVP skeleton returns deterministic stub data. Replace these methods with
    httpx calls once the Spring Boot internal tool endpoints are finalized.
    """

    def __init__(self) -> None:
        self.base_url = get_settings().spring_api_base_url.rstrip("/")

    def search_properties(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "properties": [
                {
                    "id": 1,
                    "buildingName": "관악 샘플 원룸",
                    "address": "서울특별시 관악구 대학동",
                    "propertyType": "ONE_ROOM",
                    "transactionType": "MONTHLY_RENT",
                    "deposit": 5000000,
                    "monthlyRent": 480000,
                    "areaM2": 22.5,
                    "safetyScore": 78,
                    "latitude": 37.470123,
                    "longitude": 126.936456,
                }
            ],
            "meta": {
                "baseUrl": self.base_url,
                "query": message,
                "selectedPropertyId": context.get("selectedPropertyId"),
                "stub": True,
            },
        }

    def analyze_price(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "baseUrl": self.base_url,
            "query": message,
            "selectedPropertyId": context.get("selectedPropertyId"),
            "summary": "주변 실거래가 대비 가격 적정성을 Spring Boot API에서 조회할 예정입니다.",
            "stub": True,
        }

    def analyze_safety(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "baseUrl": self.base_url,
            "query": message,
            "selectedPropertyId": context.get("selectedPropertyId"),
            "summary": "반경 내 CCTV, 비상벨, 보안등, 파출소 밀도를 Spring Boot API에서 조회할 예정입니다.",
            "stub": True,
        }
