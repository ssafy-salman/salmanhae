"""
supervisor 도입 전/후 성능 비교용 eval 데이터셋.

is_complex=True 케이스는 현재 단일 intent 구조로는 완전히 처리할 수 없는 복합 의도 질의.
supervisor 패턴 도입 후 동일 케이스를 실행해 workers_called와 비교한다.
"""

from dataclasses import dataclass


@dataclass
class EvalCase:
    message: str
    expected_workers: list[str]  # 필요한 워커 목록 (순서 무관)
    is_complex: bool = False
    note: str = ""


EVAL_SET: list[EvalCase] = [
    # ── PROPERTY_SEARCH (단순) ────────────────────────────────────────────────
    EvalCase("신림동 월세 50만원 이하 원룸 추천해줘", ["PROPERTY_SEARCH"]),
    EvalCase("관악구 오피스텔 보증금 1000만원 이하 매물 찾아줘", ["PROPERTY_SEARCH"]),
    EvalCase("강남역 근처 투룸 전세 있어?", ["PROPERTY_SEARCH"]),
    EvalCase("빌라 말고 아파트 월세로 구하고 싶어", ["PROPERTY_SEARCH"]),
    EvalCase("역세권 오피스텔 전세 매물 보여줘", ["PROPERTY_SEARCH"]),

    # ── LEGAL_CONSULT (단순) ──────────────────────────────────────────────────
    EvalCase("전세 계약 만료 전에 해지하려면 어떻게 해야 해?", ["LEGAL_CONSULT"]),
    EvalCase("보증금 못 받을 것 같은데 어떻게 대응해?", ["LEGAL_CONSULT"]),
    EvalCase("계약갱신청구권 한 번 썼으면 또 쓸 수 있어?", ["LEGAL_CONSULT"]),
    EvalCase("확정일자랑 전입신고 뭐가 다른 거야?", ["LEGAL_CONSULT"]),
    EvalCase("묵시적 갱신이 되면 계약 기간이 어떻게 돼?", ["LEGAL_CONSULT"]),

    # ── PRICE_ANALYSIS (단순) ─────────────────────────────────────────────────
    EvalCase("관악구 오피스텔 요즘 전세 시세 어때?", ["PRICE_ANALYSIS"]),
    EvalCase("강남구 아파트 최근 실거래가 추이 알려줘", ["PRICE_ANALYSIS"]),
    EvalCase("이 매물 가격이 주변 시세 대비 적정한지 분석해줘", ["PRICE_ANALYSIS"]),
    EvalCase("신림동 원룸 평균 월세가 얼마야?", ["PRICE_ANALYSIS"]),

    # ── SAFETY_ANALYSIS (단순) ────────────────────────────────────────────────
    EvalCase("신림동 밤에 혼자 다녀도 안전한 동네야?", ["SAFETY_ANALYSIS"]),
    EvalCase("관악구 CCTV 많이 설치된 동네 알려줘", ["SAFETY_ANALYSIS"]),
    EvalCase("이 동네 치안 점수 어때?", ["SAFETY_ANALYSIS"]),
    EvalCase("반경 500m 내 안전시설 얼마나 있어?", ["SAFETY_ANALYSIS"]),

    # ── GENERAL_CHAT (단순) ───────────────────────────────────────────────────
    EvalCase("안녕", ["GENERAL_CHAT"]),
    EvalCase("고마워 도움 많이 됐어", ["GENERAL_CHAT"]),
    EvalCase("살만해 서비스가 뭐야?", ["GENERAL_CHAT"]),

    # ── 복합: PROPERTY_SEARCH + PRICE_ANALYSIS ────────────────────────────────
    EvalCase(
        "강남구 오피스텔 가장 싼 거 추천해줘",
        ["PRICE_ANALYSIS", "PROPERTY_SEARCH"],
        is_complex=True,
        note="시세 파악 후 조건에 맞는 매물 검색",
    ),
    EvalCase(
        "시세 대비 저렴하게 나온 신림동 원룸 찾아줘",
        ["PRICE_ANALYSIS", "PROPERTY_SEARCH"],
        is_complex=True,
        note="시세 비교 후 매물 추천",
    ),
    EvalCase(
        "관악구에서 가성비 좋은 오피스텔 매물 알려줘",
        ["PRICE_ANALYSIS", "PROPERTY_SEARCH"],
        is_complex=True,
        note="가성비 = 시세 + 매물",
    ),
    EvalCase(
        "요즘 시세보다 싸게 나온 매물 있어?",
        ["PRICE_ANALYSIS", "PROPERTY_SEARCH"],
        is_complex=True,
        note="시세 기준 비교 후 매물 탐색",
    ),
    EvalCase(
        "실거래가 기준으로 합리적인 가격대 오피스텔 추천해줘",
        ["PRICE_ANALYSIS", "PROPERTY_SEARCH"],
        is_complex=True,
        note="실거래가 분석 + 매물 검색",
    ),

    # ── 복합: PROPERTY_SEARCH + SAFETY_ANALYSIS ───────────────────────────────
    EvalCase(
        "신림동에서 안전하고 저렴한 원룸 찾아줘",
        ["SAFETY_ANALYSIS", "PROPERTY_SEARCH"],
        is_complex=True,
        note="안전 분석 + 매물 검색",
    ),
    EvalCase(
        "혼자 사는 여성인데 안전한 동네 오피스텔 구해줘",
        ["SAFETY_ANALYSIS", "PROPERTY_SEARCH"],
        is_complex=True,
        note="치안 우선 + 매물 검색",
    ),
    EvalCase(
        "CCTV 많고 경찰서 가까운 동네 월세 매물 찾아줘",
        ["SAFETY_ANALYSIS", "PROPERTY_SEARCH"],
        is_complex=True,
        note="안전시설 조건 + 매물",
    ),
    EvalCase(
        "밤에 혼자 다녀도 안전한 곳에 있는 원룸 추천해줘",
        ["SAFETY_ANALYSIS", "PROPERTY_SEARCH"],
        is_complex=True,
        note="안전 평가 후 매물 추천",
    ),

    # ── 복합: PROPERTY_SEARCH + LEGAL_CONSULT ────────────────────────────────
    EvalCase(
        "관악구에서 전세사기 위험 없는 매물 추천해줘",
        ["LEGAL_CONSULT", "PROPERTY_SEARCH"],
        is_complex=True,
        note="법적 리스크 파악 + 매물 검색",
    ),
    EvalCase(
        "법적으로 안전한 전세 집 구하고 싶어",
        ["LEGAL_CONSULT", "PROPERTY_SEARCH"],
        is_complex=True,
        note="법률 안전성 확인 + 매물 탐색",
    ),
    EvalCase(
        "확정일자 받기 좋은 조건의 매물 찾아줘",
        ["LEGAL_CONSULT", "PROPERTY_SEARCH"],
        is_complex=True,
        note="법률 조건 + 매물",
    ),

    # ── 복합: SAFETY_ANALYSIS + PRICE_ANALYSIS ───────────────────────────────
    EvalCase(
        "강남구에서 치안 좋고 시세도 합리적인 동네 알려줘",
        ["SAFETY_ANALYSIS", "PRICE_ANALYSIS"],
        is_complex=True,
        note="안전 + 시세 지역 분석",
    ),
    EvalCase(
        "안전하면서 집값이 너무 비싸지 않은 지역 추천해줘",
        ["SAFETY_ANALYSIS", "PRICE_ANALYSIS"],
        is_complex=True,
        note="치안 + 가격 지역 비교",
    ),

    # ── 복합: PROPERTY + SAFETY + PRICE (3개) ────────────────────────────────
    EvalCase(
        "강남구 치안 좋고 가격 합리적인 오피스텔 추천해줘",
        ["SAFETY_ANALYSIS", "PRICE_ANALYSIS", "PROPERTY_SEARCH"],
        is_complex=True,
        note="치안 + 시세 + 매물 3종",
    ),
    EvalCase(
        "보증금 5000만원 이하로 치안 좋은 동네 원룸 구하고 싶어",
        ["SAFETY_ANALYSIS", "PRICE_ANALYSIS", "PROPERTY_SEARCH"],
        is_complex=True,
        note="가격 조건 + 안전 + 매물",
    ),
    EvalCase(
        "안전하고 시세 대비 저렴한 신림동 매물 보여줘",
        ["SAFETY_ANALYSIS", "PRICE_ANALYSIS", "PROPERTY_SEARCH"],
        is_complex=True,
        note="안전 + 시세비교 + 매물",
    ),
]
