from app.graph.nodes import safety_analysis as safety_analysis_module
from app.graph.nodes.safety_analysis import safety_analysis
from app.graph.state import Intent
from app.services.analysis_answer_service import AnalysisAnswerService


def test_safety_analysis_uses_precomputed_spring_summary(monkeypatch) -> None:
    class FakeSpringClient:
        def analyze_safety(self, message: str, context: dict) -> dict:
            assert message == "이 매물 주변 안전은 어때?"
            assert context["selectedPropertyId"] == "7"
            return {
                "selectedPropertyId": "7",
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
                    "propertyId": 7,
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

    state = safety_analysis(
        {
            "user_id": "user-1",
            "session_id": None,
            "message": "이 매물 주변 안전은 어때?",
            "context": {"selectedPropertyId": "7"},
            "intent": Intent.SAFETY_ANALYSIS,
            "workers_called": [],
            "analysis_cards": [],
            "tool_results": {},
        }
    )

    card = state["analysis_cards"][0]
    assert card["type"] == "SAFETY"
    assert card["title"] == "안전 분석"
    assert card["summary"] == "반경 500m 기준 안전 점수는 78점입니다."
    assert card["score"] == 78
    assert card["metrics"]["radius"] == 500
    assert card["metrics"]["cctvCount300m"] == 8
    assert state["tool_results"]["safetyAnalysis"]["safetySummary"]["safetyScore"] == 78

    answer = AnalysisAnswerService().generate_safety_answer(state)
    assert "안전 점수 78점" in answer
    assert "비상벨 2개" in answer
    assert "보안등 14개" in answer
    assert "경찰시설 1개" in answer


def test_safety_answer_handles_missing_summary() -> None:
    answer = AnalysisAnswerService().generate_safety_answer(
        {
            "user_id": "user-1",
            "session_id": None,
            "message": "안전 분석해줘",
            "context": {},
            "intent": Intent.SAFETY_ANALYSIS,
            "analysis_cards": [],
            "tool_results": {"safetyAnalysis": {"metrics": {}}},
        }
    )

    assert answer == "분석할 근거 데이터가 부족합니다. 매물을 선택하거나 안전 데이터가 쌓인 뒤 다시 확인해 주세요."
