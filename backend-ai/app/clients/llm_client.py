from app.graph.state import AgentState, Intent
from app.rag.prompts import format_legal_context


class LLMClient:
    """GMS LLM API boundary.

    The current implementation stays deterministic for tests. The public method
    signature should remain stable when the live LLM call is wired in.
    """

    def generate_answer(self, state: AgentState) -> str:
        intent = state.get("intent", Intent.FALLBACK)
        if intent == Intent.PROPERTY_SEARCH:
            count = len(state.get("properties", []))
            return f"조건에 맞는 매물 {count}개를 찾았습니다."
        if intent == Intent.LEGAL_CONSULT:
            return generate_legal_answer(state)
        if intent == Intent.PRICE_ANALYSIS:
            return "선택한 매물 또는 지역의 실거래가를 기준으로 시세 적정성을 분석했습니다."
        if intent == Intent.SAFETY_ANALYSIS:
            return "주변 안전시설 반경과 안전 점수를 기준으로 생활 안전성을 분석했습니다."
        if intent == Intent.HUG_CALC:
            return "HUG 보증 가입 계산은 1.5차 범위입니다. MVP에서는 관련 조건 안내까지만 제공합니다."
        return "질문 의도를 조금 더 구체화해 주세요. 매물 추천, 법률 상담, 시세 분석, 안전 분석을 도와드릴 수 있습니다."


def generate_legal_answer(state: AgentState) -> str:
    legal_cards = state.get("legal_cards", [])
    if not legal_cards:
        return (
            "검색된 법령 근거가 없습니다. 질문을 조금 더 구체화하거나 계약서와 상황을 정리해 "
            "전문가 검토를 받아보는 것을 권장합니다."
        )

    legal_context = format_legal_context(legal_cards)

    return (
        "검색된 법령 근거를 바탕으로 답변드리면 다음과 같습니다.\n\n"
        + legal_context
        + "\n\n위 조항은 질문 상황을 판단할 때 참고할 수 있는 근거입니다. "
        "실제 계약 체결이나 분쟁 대응 전에는 계약서 원문과 사실관계를 가지고 전문가 검토를 받는 것을 권장합니다."
    )
