from app.graph.state import AgentState, Intent


class LLMClient:
    """GMS LLM API boundary.

    This stub keeps tests deterministic. The public method signature should stay
    stable when the real GMS API spec is wired in.
    """

    def generate_answer(self, state: AgentState) -> str:
        intent = state.get("intent", Intent.FALLBACK)
        if intent == Intent.PROPERTY_SEARCH:
            count = len(state.get("properties", []))
            return f"조건에 맞는 매물 {count}개를 찾았습니다."
        if intent == Intent.LEGAL_CONSULT:
            count = len(state.get("legal_cards", []))
            return f"관련 법령 근거 {count}개를 확인했습니다. 실제 계약 전에는 전문가 검토도 함께 권장합니다."
        if intent == Intent.PRICE_ANALYSIS:
            return "선택한 매물 또는 지역의 실거래가를 기준으로 시세 적정성을 분석할 수 있습니다."
        if intent == Intent.SAFETY_ANALYSIS:
            return "주변 안전시설 밀도와 안전 점수를 기준으로 생활 안전성을 분석할 수 있습니다."
        if intent == Intent.HUG_CALC:
            return "HUG 보증 간이 계산은 1.5차 범위입니다. MVP에서는 관련 조건 안내까지만 제공합니다."
        return "질문 의도를 조금 더 구체화해 주세요. 매물 추천, 법률 상담, 시세 분석, 안전 분석을 도와드릴 수 있습니다."
