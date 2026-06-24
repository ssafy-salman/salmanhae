import json
from collections.abc import Callable
from typing import Any

import httpx

from app.core.config import get_settings
from app.graph.state import AgentState
from app.rag.prompts import (
    build_analysis_answer_prompt,
    build_legal_rag_prompt,
    format_legal_context,
)
from app.services.analysis_answer_service import AnalysisAnswerService


HttpPost = Callable[..., httpx.Response]

SUPERVISOR_PROMPT = """\
다음 사용자 메시지와 지금까지 실행된 워커 목록을 보고, 다음에 호출할 워커를 결정해줘.

사용자 메시지: {message}
이미 실행된 워커: {workers_called}

사용 가능한 워커:
- PROPERTY_SEARCH: 매물 추천·검색·조건 필터링 (지역, 가격, 면적, 타입 등)
- LEGAL_CONSULT: 임대차 법률, 계약, 보증금, 대항력, 갱신 등 법률 질문
- PRICE_ANALYSIS: 특정 지역·매물의 시세·실거래가·가격 적정성 분석
- SAFETY_ANALYSIS: 주변 치안, CCTV, 안전시설, 범죄율 등 생활 안전 분석
- FINISH: 충분한 정보가 모였으므로 답변 생성 단계로 이동

규칙:
- 이미 실행된 워커는 다시 선택하지 마.
- 사용자 의도를 처리하기에 충분한 워커가 실행됐으면 FINISH를 선택해.
- 워커가 하나도 실행되지 않았으면 반드시 워커 하나를 선택해.

JSON만 반환해. 설명 없이:
{{"next_worker": "...", "reasoning": "이유 한 줄"}}\
"""

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

    def decide_next_worker(self, message: str, workers_called: list[str]) -> str:
        prompt = SUPERVISOR_PROMPT.format(
            message=message,
            workers_called=", ".join(workers_called) if workers_called else "없음",
        )
        valid = {"PROPERTY_SEARCH", "LEGAL_CONSULT", "PRICE_ANALYSIS", "SAFETY_ANALYSIS", "FINISH"}
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
            next_worker = parsed.get("next_worker", "FINISH")
            if next_worker not in valid or next_worker in workers_called:
                return "FINISH"
            return next_worker
        except (httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            return "FINISH"

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
            return AnalysisAnswerService().generate_price_answer(state)
        if intent == Intent.SAFETY_ANALYSIS:
            live_answer = self._generate_live_analysis_answer(state)
            if live_answer:
                return live_answer
            return AnalysisAnswerService().generate_safety_answer(state)
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

        try:
            prompt = build_analysis_answer_prompt(
                state["message"],
                analysis_cards,
                json.dumps(tool_results, ensure_ascii=False),
            )
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
