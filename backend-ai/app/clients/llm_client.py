from collections.abc import Callable
from typing import Any

import httpx

from app.core.config import get_settings
from app.graph.state import AgentState, Intent
from app.rag.prompts import build_legal_rag_prompt, format_legal_context


HttpPost = Callable[..., httpx.Response]


class LLMClient:
    """GMS LLM API boundary.

    Live calls use an OpenAI-compatible chat-completions endpoint. The
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
            return "선택한 매물 또는 지역의 실거래가를 기준으로 시세 적정성을 분석했습니다."
        if intent == Intent.SAFETY_ANALYSIS:
            return "주변 안전시설 반경과 안전 점수를 기준으로 생활 안전성을 분석했습니다."
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
