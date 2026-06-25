import re
from typing import Any

from app.clients.spring_client import SpringClient
from app.clients.supabase_client import SupabaseVectorClient
from app.graph.state import AgentState


def price_analysis(state: AgentState) -> AgentState:
    client = SpringClient()
    result = client.analyze_price(
        message=state["message"],
        context=state.get("context", {}),
    )

    if result.get("requiresSelection"):
        result = _regional_price_analysis(state["message"])

    updated_tool_results = {
        **state.get("tool_results", {}),
        "priceAnalysis": result,
    }

    if result.get("requiresSelection"):
        return {**state, "tool_results": updated_tool_results}

    metrics = {
        "selectedPropertyId": result.get("selectedPropertyId"),
        "stub": result.get("stub", False),
        **result.get("metrics", {}),
    }
    if result.get("error"):
        metrics["error"] = result["error"]

    analysis_card = {
        "type": "PRICE",
        "title": "시세 분석",
        "summary": result["summary"],
        "score": result.get("score"),
        "metrics": metrics,
    }
    return {
        **state,
        "analysis_cards": [*state.get("analysis_cards", []), analysis_card],
        "tool_results": updated_tool_results,
    }


def _regional_price_analysis(message: str) -> dict[str, Any]:
    criteria = _extract_region_criteria(message)
    sigungu = criteria.get("sigungu")
    dong = criteria.get("dong")

    if not sigungu and not dong:
        return {
            "requiresSelection": True,
            "summary": "시세를 조회할 지역명을 알려주세요. 예) '관악구 시세 어때?'",
            "metrics": {},
        }

    try:
        db = SupabaseVectorClient()
        stats = db.get_regional_price_stats(
            sigungu=sigungu,
            dong=dong,
            property_type=criteria.get("property_type"),
            transaction_type=criteria.get("transaction_type"),
        )
    except Exception as exc:
        return {
            "error": "DB_UNAVAILABLE",
            "errorDetail": str(exc),
            "summary": "시세 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.",
            "metrics": {},
            "stub": False,
        }

    region_name = dong or sigungu
    if not stats:
        return {
            "summary": f"{region_name} 지역의 시세 데이터가 없습니다.",
            "regionalStats": [],
            "metrics": {"regionStatCount": 0},
            "stub": False,
        }

    return {
        "summary": f"{region_name} 지역 시세 통계 {len(stats)}건을 확인했습니다.",
        "regionalStats": [dict(row) for row in stats],
        "metrics": {
            "regionStatCount": len(stats),
            "sigungu": sigungu,
            "dong": dong,
        },
        "stub": False,
    }


def _extract_region_criteria(message: str) -> dict[str, str | None]:
    property_type = None
    if "원룸" in message:
        property_type = "ONE_ROOM"
    elif "오피스텔" in message:
        property_type = "OFFICETEL"
    elif "빌라" in message:
        property_type = "VILLA"
    elif "아파트" in message:
        property_type = "APARTMENT"
    elif "다가구" in message:
        property_type = "MULTI_FAMILY"

    transaction_type = None
    if "전세" in message:
        transaction_type = "JEONSE"
    elif "월세" in message:
        transaction_type = "MONTHLY_RENT"
    elif "매매" in message:
        transaction_type = "SALE"

    sigungu = None
    dong = None
    for word in re.findall(r"[가-힣]+", message):
        if not sigungu and len(word) >= 2 and word[-1] in ("구", "군", "시"):
            sigungu = word
        elif not dong and len(word) >= 3 and word.endswith("동"):
            dong = word

    return {
        "sigungu": sigungu,
        "dong": dong,
        "property_type": property_type,
        "transaction_type": transaction_type,
    }
