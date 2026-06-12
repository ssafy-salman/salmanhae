from app.graph.state import AgentState, Intent


LEGAL_KEYWORDS = [
    "법",
    "계약",
    "임대차",
    "대항력",
    "확정일자",
    "보증금 반환",
    "전세사기",
    "묵시적 갱신",
]
PRICE_KEYWORDS = ["시세", "실거래", "가격", "비싼", "싼", "평균가", "전고점"]
SAFETY_KEYWORDS = ["안전", "치안", "cctv", "비상벨", "보안등", "파출소", "범죄"]
HUG_KEYWORDS = ["hug", "보증보험", "보증 가능", "보증 가입", "보증금 보험"]
PROPERTY_KEYWORDS = ["추천", "찾아", "매물", "원룸", "오피스텔", "아파트", "월세", "전세", "관악구"]


def classify_message(message: str) -> Intent:
    normalized = message.lower()
    if any(keyword in normalized for keyword in LEGAL_KEYWORDS):
        return Intent.LEGAL_CONSULT
    if any(keyword in normalized for keyword in HUG_KEYWORDS):
        return Intent.HUG_CALC
    if any(keyword in normalized for keyword in PRICE_KEYWORDS):
        return Intent.PRICE_ANALYSIS
    if any(keyword in normalized for keyword in SAFETY_KEYWORDS):
        return Intent.SAFETY_ANALYSIS
    if any(keyword in normalized for keyword in PROPERTY_KEYWORDS):
        return Intent.PROPERTY_SEARCH
    return Intent.FALLBACK


def classify_intent(state: AgentState) -> AgentState:
    return {**state, "intent": classify_message(state["message"])}
