import json
from collections.abc import Callable
from typing import Any

import httpx

from app.core.config import get_settings
from app.graph.state import AgentState, Intent
from app.rag.prompts import (
    build_analysis_answer_prompt,
    build_legal_rag_prompt,
    format_legal_context,
)


HttpPost = Callable[..., httpx.Response]

CLASSIFY_INTENT_PROMPT = """\
다음 사용자 메시지를 읽고, 부동산 AI 어시스턴트 관점에서 의도를 분류해줘.

사용자 메시지: {message}

다음 intent 중 하나를 선택해:
- PROPERTY_SEARCH: 매물 추천·검색·조건 필터링 (지역, 가격, 면적, 타입 등)
- LEGAL_CONSULT: 임대차 법률, 계약, 보증금, 대항력, 갱신 등 법률 질문
- PRICE_ANALYSIS: 특정 지역·매물의 시세·실거래가·가격 적정성 분석
- SAFETY_ANALYSIS: 주변 치안, CCTV, 안전시설, 범죄율 등 생활 안전 분석
- HUG_CALC: HUG 보증보험 가입 가능 여부 계산
- GENERAL_CHAT: 인사, 잡담, 부동산과 무관한 질문

JSON만 반환해. 설명 없이:
{{"intent": "...", "reasoning": "분류 이유 한 줄"}}\
"""

PROPERTY_CRITERIA_PROMPT = """\
다음 메시지에서 매물 검색 조건을 JSON으로 추출해줘.

메시지: {message}

아래 필드만 포함해. 언급이 없으면 null로 해:
- sigungu: 시군구 이름 (예: "관악구", "강남구")
- dong: 동 이름 (예: "신림동")
- property_type: ONE_ROOM | OFFICETEL | VILLA | APARTMENT | MULTI_FAMILY
- transaction_type: MONTHLY_RENT | JEONSE | SALE
- max_deposit: 최대 보증금 (원 단위, 숫자만)
- max_monthly_rent: 최대 월세 (원 단위, 숫자만)
- max_price: 최대 매매가 (원 단위, 숫자만)

JSON만 반환해. 설명 없이.\
"""


class LLMClient:
    """Live calls use an OpenAI-compatible chat-completions endpoint. The
    deterministic fallback keeps local development and tests usable when no LLM
    key is configured or the provider is temporarily unavailable.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout_seconds: float = 20.0,
        http_post: HttpPost = httpx.post,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.gms_api_key
        self.model = model if model is not None else settings.llm_model
        configured_base_url = base_url if base_url is not None else settings.llm_base_url
        self.base_url = configured_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.http_post = http_post

    def classify(self, message: str) -> dict[str, Any] | None:
        prompt = CLASSIFY_INTENT_PROMPT.format(message=message)
        try:
            response = self.http_post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_completion_tokens": 128,
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            text = extract_chat_completion_text(response.json()) or "{}"
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else None
        except (httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            return None

    def extract_property_criteria(self, message: str) -> dict[str, Any]:
        prompt = PROPERTY_CRITERIA_PROMPT.format(message=message)
        try:
            response = self.http_post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_completion_tokens": 256,
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            text = extract_chat_completion_text(response.json()) or "{}"
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else {}
        except (httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            return {}

    def generate_answer(self, state: AgentState) -> str:
        intent = state.get("intent", Intent.FALLBACK)
        if intent == Intent.LEGAL_CONSULT:
            live_answer = self._generate_live_legal_answer(state)
            if live_answer:
                return live_answer
            return generate_legal_answer(state)
        if intent == Intent.PROPERTY_SEARCH:
            count = len(state.get("properties", []))
            return f"조건에 맞는 매물 {count}개를 찾았습니다."
        if intent == Intent.PRICE_ANALYSIS:
            live_answer = self._generate_live_analysis_answer(state)
            if live_answer:
                return live_answer
            return generate_price_analysis_answer(state)
        if intent == Intent.SAFETY_ANALYSIS:
            live_answer = self._generate_live_analysis_answer(state)
            if live_answer:
                return live_answer
            return generate_safety_analysis_answer(state)
        if intent == Intent.HUG_CALC:
            return "HUG 보증 가입 계산은 1.5차 범위입니다. MVP에서는 관련 조건 안내까지만 제공합니다."
        return "질문 의도를 조금 더 구체화해 주세요. 매물 추천, 법률 상담, 시세 분석, 안전 분석을 도와드릴 수 있습니다."

    def _generate_live_legal_answer(self, state: AgentState) -> str | None:
        legal_cards = state.get("legal_cards", [])
        if not self.api_key or not self.model or not legal_cards:
            return None

        prompt = build_legal_rag_prompt(state["message"], legal_cards)
        try:
            response = self.http_post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You answer Korean housing lease questions only from the provided "
                                "retrieved legal references. If the references are insufficient, "
                                "say so clearly."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "max_completion_tokens": 700,
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return extract_chat_completion_text(response.json())
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            return None

    def _generate_live_analysis_answer(self, state: AgentState) -> str | None:
        analysis_cards = state.get("analysis_cards", [])
        tool_results = state.get("tool_results", {})
        if not self.api_key or not self.model or not analysis_cards or not tool_results:
            return None

        prompt = build_analysis_answer_prompt(
            state["message"],
            analysis_cards,
            json.dumps(tool_results, ensure_ascii=False),
        )
        try:
            response = self.http_post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_completion_tokens": 500,
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return extract_chat_completion_text(response.json())
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            return None


def extract_chat_completion_text(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None

    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return None

    message = choices[0].get("message")
    if not isinstance(message, dict):
        return None

    content = message.get("content")
    if isinstance(content, str):
        stripped = content.strip()
        return stripped or None

    if isinstance(content, list):
        parts = [
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") in {"text", "output_text"}
        ]
        stripped = "\n".join(part for part in parts if part).strip()
        return stripped or None

    return None


def generate_price_analysis_answer(state: AgentState) -> str:
    result = _tool_result(state, "priceAnalysis")
    card = _analysis_card(state, "PRICE")
    metrics = _combined_metrics(result, card)
    transactions = _items(result.get("transactions"))
    price_analysis = result.get("priceAnalysis", {})
    if not isinstance(price_analysis, dict):
        price_analysis = {}
    region_stats = _items(price_analysis.get("regionStats"))

    facts: list[str] = []
    comparable_count = metrics.get("comparableTransactionCount") or len(transactions)
    if comparable_count:
        facts.append(f"최근 실거래 {comparable_count}건을 기준으로 확인했습니다.")

    if transactions:
        transaction = transactions[0]
        parts: list[str] = []
        contract_ym = transaction.get("contractYearMonth")
        if contract_ym:
            parts.append(str(contract_ym))
        deposit = _format_won(transaction.get("deposit"))
        if deposit:
            parts.append(f"보증금 {deposit}")
        monthly_rent = _format_won(transaction.get("monthlyRent"))
        if monthly_rent:
            parts.append(f"월세 {monthly_rent}")
        area_m2 = transaction.get("areaM2")
        if area_m2 is not None:
            parts.append(f"전용면적 {area_m2}㎡")
        if parts:
            facts.append("최근 사례는 " + ", ".join(parts) + "입니다.")

    if region_stats:
        region_stat = region_stats[0]
        parts = []
        avg_deposit = _format_won(region_stat.get("avgDeposit"))
        if avg_deposit:
            parts.append(f"지역 평균 보증금 {avg_deposit}")
        avg_monthly_rent = _format_won(region_stat.get("avgMonthlyRent"))
        if avg_monthly_rent:
            parts.append(f"지역 평균 월세 {avg_monthly_rent}")
        transaction_count = region_stat.get("transactionCount")
        if transaction_count:
            parts.append(f"통계 표본 {transaction_count}건")
        if parts:
            facts.append(", ".join(parts) + "입니다.")

    if not facts:
        return "분석할 근거 데이터가 부족합니다. 매물을 선택하거나 시세 데이터가 쌓인 뒤 다시 확인해 주세요."

    return " ".join(facts) + " 보증보험 가능 여부나 법적 판단은 포함하지 않습니다."


def generate_safety_analysis_answer(state: AgentState) -> str:
    result = _tool_result(state, "safetyAnalysis")
    card = _analysis_card(state, "SAFETY")
    safety_summary = result.get("safetySummary", {})
    if not isinstance(safety_summary, dict):
        safety_summary = {}
    metrics = {**safety_summary, **_combined_metrics(result, card)}

    facts: list[str] = []
    score = (
        result.get("score")
        or card.get("score")
        or safety_summary.get("safetyScore")
        or metrics.get("safetyScore")
    )
    if score is not None:
        facts.append(f"안전 점수 {score}점")

    radius = metrics.get("radius")
    if radius is not None:
        facts.append(f"반경 {radius}m")

    count_specs = [
        ("cctvCount300m", "CCTV"),
        ("bellCount300m", "비상벨"),
        ("lightCount300m", "보안등"),
        ("policeCount500m", "파출소"),
    ]
    for key, label in count_specs:
        value = metrics.get(key)
        if value is not None:
            facts.append(f"{label} {value}개")

    if not facts:
        return "분석할 근거 데이터가 부족합니다. 매물을 선택하거나 안전 데이터가 쌓인 뒤 다시 확인해 주세요."

    return "주변 안전 데이터는 " + ", ".join(facts) + "로 확인됩니다. 실제 체감 안전은 현장 환경에 따라 달라질 수 있습니다."


def _tool_result(state: AgentState, key: str) -> dict[str, Any]:
    tool_results = state.get("tool_results", {})
    if not isinstance(tool_results, dict):
        return {}
    value = tool_results.get(key, {})
    return value if isinstance(value, dict) else {}


def _analysis_card(state: AgentState, card_type: str) -> dict[str, Any]:
    analysis_cards = state.get("analysis_cards", [])
    if not isinstance(analysis_cards, list):
        return {}
    for card in analysis_cards:
        if isinstance(card, dict) and card.get("type") == card_type:
            return card
    return {}


def _combined_metrics(result: dict[str, Any], card: dict[str, Any]) -> dict[str, Any]:
    result_metrics = result.get("metrics", {})
    card_metrics = card.get("metrics", {})
    if not isinstance(result_metrics, dict):
        result_metrics = {}
    if not isinstance(card_metrics, dict):
        card_metrics = {}
    return {**result_metrics, **card_metrics}


def _items(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _format_won(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            return None
    if not isinstance(value, (int, float)):
        return None
    amount = int(value) if float(value).is_integer() else value
    return f"{amount:,}원"


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
