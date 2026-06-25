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
RENDERABLE_WORKERS = {
    "PROPERTY_SEARCH",
    "LEGAL_CONSULT",
    "PRICE_ANALYSIS",
    "SAFETY_ANALYSIS",
    "GENERAL_CHAT",
}

SUPERVISOR_PROMPT = """\
다음 사용자 메시지와 지금까지 실행된 워커 목록을 보고, 다음에 호출할 워커를 결정해줘.

사용자 메시지: {message}
이미 실행된 워커: {workers_called}

사용 가능한 워커:
- PROPERTY_SEARCH: 매물 추천·검색·조건 필터링 (지역, 가격, 면적, 타입 등). "가장 싼 매물", "저렴한 원룸" 등 매물 목록을 찾는 검색도 여기에 해당.
- LEGAL_CONSULT: 임대차 법률, 계약, 보증금, 대항력, 갱신 등 법률 질문
- PRICE_ANALYSIS: 특정 지역 또는 선택된 매물의 실거래가·시세·가격 동향 분석. "관악구 시세", "아파트 최근 거래가", "전세 평균 얼마야" 등 가격 데이터 조회.
- SAFETY_ANALYSIS: 특정 지역 또는 선택된 매물 주변의 치안·CCTV·안전시설 분석.
- GENERAL_CHAT: 인사, 잡담, 서비스 소개 등 부동산과 무관한 일반 대화
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
- sort_by: "price_asc" (가장 싼, 저렴한, 싼 순, 최저가 등 저가 정렬 요청 시) | null (그 외)
- limit: 사용자가 명시적으로 개수를 요청한 경우 해당 숫자 (예: "1개", "3개 보여줘") | null (그 외)

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
        valid = {"PROPERTY_SEARCH", "LEGAL_CONSULT", "PRICE_ANALYSIS", "SAFETY_ANALYSIS", "GENERAL_CHAT", "FINISH"}
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
            # 아직 아무 워커도 실행되지 않은 첫 호출에서 장애가 나면 FINISH로 보내면
            # workers_called=[]인 채로 generate_answer에 도달해 fallback 메시지만 반환됨.
            # 기본 워커로 라우팅해 최소한의 응답을 보장한다.
            if not workers_called:
                return "PROPERTY_SEARCH"
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
        workers_called = state.get("workers_called", [])
        if not workers_called and state.get("intent"):
            intent = state["intent"]
            intent_worker = str(getattr(intent, "value", intent))
            if intent_worker in RENDERABLE_WORKERS:
                workers_called = [intent_worker]

        if "GENERAL_CHAT" in workers_called:
            live = self._generate_live_general_chat_answer(state)
            if live:
                return live
            return "안녕하세요! 살만해 부동산 AI입니다. 매물 추천, 법률 상담, 시세 분석, 안전 분석을 도와드릴 수 있습니다."

        parts: list[str] = []

        if "LEGAL_CONSULT" in workers_called:
            live_answer = self._generate_live_legal_answer(state)
            parts.append(live_answer if live_answer else generate_legal_answer(state))

        if "PRICE_ANALYSIS" in workers_called or "SAFETY_ANALYSIS" in workers_called:
            live_answer = self._generate_live_analysis_answer(state)
            if live_answer:
                parts.append(live_answer)
            else:
                if "PRICE_ANALYSIS" in workers_called:
                    parts.append(AnalysisAnswerService().generate_price_answer(state))
                if "SAFETY_ANALYSIS" in workers_called:
                    parts.append(AnalysisAnswerService().generate_safety_answer(state))

        if "PROPERTY_SEARCH" in workers_called:
            properties = state.get("properties", [])
            count = len(properties)
            if count == 0:
                parts.append(
                    "조건에 맞는 매물이 없습니다. "
                    "지역명, 매물 유형(원룸·오피스텔·아파트 등), 거래 유형(월세·전세·매매)을 바꿔서 다시 검색해 보세요."
                )
            else:
                live = self._generate_live_property_search_answer(state)
                base = live if live else f"조건에 맞는 매물 {count}개를 찾았습니다."
                parts.append(base + "\n아래 매물 중 하나를 선택하면 시세·안전 분석을 해 드릴게요.")

        if parts:
            return "\n\n".join(parts)

        return "질문 의도를 조금 더 구체화해 주세요. 매물 추천, 법률 상담, 시세 분석, 안전 분석을 도와드릴 수 있습니다."

    def _generate_live_general_chat_answer(self, state: AgentState) -> str | None:
        if not self.api_key or not self.model:
            return None
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
                                "당신은 살만해 부동산 AI 어시스턴트입니다. "
                                "매물 추천, 임대차 법률 상담, 시세 분석, 안전 분석을 도와줍니다. "
                                "일반 대화나 인사에는 친절하게 응답하고, 부동산 관련 질문으로 자연스럽게 유도하세요. "
                                "한국어로 간결하게 답변하세요."
                            ),
                        },
                        {"role": "user", "content": state["message"]},
                    ],
                    "max_completion_tokens": 300,
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return extract_chat_completion_text(response.json())
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            return None

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

    def _generate_live_property_search_answer(self, state: AgentState) -> str | None:
        properties = state.get("properties", [])
        if not self.api_key or not self.model or not properties:
            return None

        type_labels = {
            "ONE_ROOM": "원룸", "OFFICETEL": "오피스텔", "VILLA": "빌라",
            "APARTMENT": "아파트", "MULTI_FAMILY": "다가구",
        }
        tx_labels = {"MONTHLY_RENT": "월세", "JEONSE": "전세", "SALE": "매매"}

        lines = []
        for p in properties[:5]:
            name = p.get("building_name") or p.get("title") or "매물"
            pt = type_labels.get(str(p.get("property_type", "")), "")
            tx = tx_labels.get(str(p.get("transaction_type", "")), "")
            deposit = p.get("deposit")
            rent = p.get("monthly_rent")
            price = p.get("price")
            if tx == "월세" and deposit is not None and rent is not None:
                price_str = f"{int(deposit) // 10000:,}/{int(rent) // 10000:,}만원"
            elif tx == "전세" and deposit is not None:
                price_str = f"전세 {int(deposit) // 10000:,}만원"
            elif tx == "매매" and price is not None:
                price_str = f"매매 {int(price) // 10000:,}만원"
            else:
                price_str = ""
            tag = " · ".join(x for x in [pt, tx, price_str] if x)
            lines.append(f"- {name} ({tag})")

        prop_summary = "\n".join(lines)
        total = len(properties)

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
                                "당신은 살만해 부동산 AI입니다. "
                                "검색된 매물 목록을 바탕으로 사용자에게 2문장으로 간결하게 안내하세요. "
                                "한국어로 답변하세요."
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                f"사용자 요청: {state['message']}\n\n"
                                f"검색 결과 총 {total}개 (상위 {len(lines)}개):\n{prop_summary}\n\n"
                                f"위 결과를 2문장으로 안내해 주세요."
                            ),
                        },
                    ],
                    "max_completion_tokens": 150,
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
