from app.clients.llm_client import LLMClient
from app.graph.state import Intent


def test_llm_client_generates_price_answer_from_tool_results() -> None:
    answer = LLMClient(api_key="").generate_answer(
        {
            "user_id": "user-1",
            "session_id": None,
            "message": "이 매물 가격이 비싼 편이야?",
            "context": {"selectedPropertyId": "1"},
            "intent": Intent.PRICE_ANALYSIS,
            "analysis_cards": [
                {
                    "type": "PRICE",
                    "summary": "최근 실거래와 지역 통계를 확인했습니다.",
                    "metrics": {
                        "selectedPropertyId": "1",
                        "comparableTransactionCount": 2,
                        "regionStatCount": 1,
                    },
                }
            ],
            "tool_results": {
                "priceAnalysis": {
                    "selectedPropertyId": "1",
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
                                "regionLevel": "DONG",
                                "avgDeposit": 10500000,
                                "avgMonthlyRent": 520000,
                                "transactionCount": 3,
                            }
                        ],
                        "buildingStats": [],
                    },
                    "metrics": {
                        "comparableTransactionCount": 2,
                        "regionStatCount": 1,
                    },
                }
            },
        }
    )

    assert "최근 실거래 2건" in answer
    assert "2026-05" in answer
    assert "보증금 10,000,000원" in answer
    assert "월세 520,000원" in answer
    assert "지역 평균 보증금 10,500,000원" in answer
    assert "HUG" not in answer


def test_llm_client_generates_safety_answer_from_tool_results() -> None:
    answer = LLMClient(api_key="").generate_answer(
        {
            "user_id": "user-1",
            "session_id": None,
            "message": "주변 안전은 어때?",
            "context": {"selectedPropertyId": "1"},
            "intent": Intent.SAFETY_ANALYSIS,
            "analysis_cards": [
                {
                    "type": "SAFETY",
                    "summary": "반경 500m 기준 안전 점수는 78점입니다.",
                    "score": 78,
                    "metrics": {
                        "selectedPropertyId": "1",
                        "radius": 500,
                        "cctvCount300m": 8,
                        "bellCount300m": 2,
                        "lightCount300m": 14,
                        "policeCount500m": 1,
                    },
                }
            ],
            "tool_results": {
                "safetyAnalysis": {
                    "selectedPropertyId": "1",
                    "score": 78,
                    "safetySummary": {
                        "radius": 500,
                        "safetyScore": 78,
                        "cctvCount300m": 8,
                        "bellCount300m": 2,
                        "lightCount300m": 14,
                        "policeCount500m": 1,
                    },
                }
            },
        }
    )

    assert "안전 점수 78점" in answer
    assert "반경 500m" in answer
    assert "CCTV 8개" in answer
    assert "비상벨 2개" in answer
    assert "보안등 14개" in answer
    assert "파출소 1개" in answer
    assert "확정" not in answer


def test_llm_client_analysis_answer_uses_controlled_fallback_without_facts() -> None:
    answer = LLMClient(api_key="").generate_answer(
        {
            "user_id": "user-1",
            "session_id": None,
            "message": "분석해줘",
            "context": {},
            "intent": Intent.PRICE_ANALYSIS,
            "analysis_cards": [],
            "tool_results": {},
        }
    )

    assert "분석할 근거 데이터가 부족합니다" in answer
    assert "HUG" not in answer


def test_llm_client_analysis_answer_prefers_current_tool_result_metrics() -> None:
    answer = LLMClient(api_key="").generate_answer(
        {
            "user_id": "user-1",
            "session_id": None,
            "message": "주변 안전은 어때?",
            "context": {"selectedPropertyId": "1"},
            "intent": Intent.SAFETY_ANALYSIS,
            "analysis_cards": [
                {
                    "type": "SAFETY",
                    "score": 12,
                    "metrics": {
                        "radius": 300,
                        "cctvCount300m": 99,
                    },
                },
                {
                    "type": "SAFETY",
                    "score": 34,
                    "metrics": {
                        "radius": 400,
                        "cctvCount300m": 55,
                    },
                },
            ],
            "tool_results": {
                "safetyAnalysis": {
                    "selectedPropertyId": "1",
                    "score": 78,
                    "metrics": {
                        "radius": 500,
                        "cctvCount300m": 8,
                    },
                }
            },
        }
    )

    assert "안전 점수 78점" in answer
    assert "반경 500m" in answer
    assert "CCTV 8개" in answer
    assert "CCTV 99개" not in answer


def test_llm_client_price_answer_preserves_zero_comparable_count() -> None:
    answer = LLMClient(api_key="").generate_answer(
        {
            "user_id": "user-1",
            "session_id": None,
            "message": "최근 거래가 있어?",
            "context": {"selectedPropertyId": "1"},
            "intent": Intent.PRICE_ANALYSIS,
            "analysis_cards": [
                {
                    "type": "PRICE",
                    "metrics": {
                        "comparableTransactionCount": 7,
                    },
                }
            ],
            "tool_results": {
                "priceAnalysis": {
                    "selectedPropertyId": "1",
                    "transactions": [
                        {
                            "contractYearMonth": "2026-05",
                            "deposit": 10000000,
                        }
                    ],
                    "metrics": {
                        "comparableTransactionCount": 0,
                    },
                }
            },
        }
    )

    assert "최근 실거래 0건" in answer
    assert "최근 실거래 1건" not in answer
    assert "최근 실거래 7건" not in answer
    assert "2026-05" in answer


def test_llm_client_safety_answer_preserves_zero_score_from_tool_result() -> None:
    answer = LLMClient(api_key="").generate_answer(
        {
            "user_id": "user-1",
            "session_id": None,
            "message": "안전 점수 알려줘",
            "context": {"selectedPropertyId": "1"},
            "intent": Intent.SAFETY_ANALYSIS,
            "analysis_cards": [
                {
                    "type": "SAFETY",
                    "score": 88,
                    "metrics": {
                        "safetyScore": 77,
                        "radius": 300,
                    },
                }
            ],
            "tool_results": {
                "safetyAnalysis": {
                    "selectedPropertyId": "1",
                    "safetySummary": {
                        "safetyScore": 0,
                        "radius": 500,
                    },
                    "metrics": {
                        "cctvCount300m": 0,
                    },
                }
            },
        }
    )

    assert "안전 점수 0점" in answer
    assert "반경 500m" in answer
    assert "CCTV 0개" in answer
    assert "88점" not in answer
    assert "77점" not in answer
    assert "반경 300m" not in answer
