# Phase 4: API 수정 + generate_answer workers_called 기반 전환

## Goal
LLMClient.generate_answer()를 intent 대신 workers_called 기반으로 변경하고, API 응답 스키마에서 intent를 제거하고 workers_called를 추가한다.

## Files
- `backend-ai/app/clients/llm_client.py` — classify() 제거, generate_answer() workers_called 기반으로 변경
- `backend-ai/app/api/schemas.py` — intent 필드 제거, workers_called 추가
- `backend-ai/app/api/routes.py` — workers_called 사용으로 변경

## Done When
- [ ] `LLMClient.classify()` 메서드가 없음 (CLASSIFY_INTENT_PROMPT도 제거)
- [ ] `LLMClient.generate_answer()`가 `state.get("workers_called", [])` 기반으로 분기함
- [ ] `AgentChatResponse`에 `intent` 필드가 없고 `workers_called: list[str]` 필드가 있음
- [ ] `routes.py`가 `result.get("workers_called", [])` 를 사용함
- [ ] `cd backend-ai && .venv/bin/python -c "from app.api.schemas import AgentChatResponse; print('ok')"` 성공

## Architecture Rules
- CLAUDE.md: Controller/Router는 입력 검증과 위임만 한다.
- CLAUDE.md: API 응답 형식 변경 시 docs/08_API_SPEC.md를 반드시 업데이트한다.

## Implementation Instructions

### 1. `backend-ai/app/clients/llm_client.py` 수정

**제거할 항목:**
- `CLASSIFY_INTENT_PROMPT` 상수 전체 삭제
- `LLMClient.classify()` 메서드 전체 삭제
- `from app.graph.state import AgentState, Intent` 에서 `Intent` 제거 → `from app.graph.state import AgentState`

**`generate_answer()` 메서드 교체:**

현재:
```python
def generate_answer(self, state: AgentState) -> str:
    intent = state.get("intent", Intent.FALLBACK)
    if intent == Intent.LEGAL_CONSULT:
        ...
    if intent == Intent.PROPERTY_SEARCH:
        ...
    if intent == Intent.PRICE_ANALYSIS:
        ...
    if intent == Intent.SAFETY_ANALYSIS:
        ...
    if intent == Intent.HUG_CALC:
        ...
    return "질문 의도를 조금 더 구체화해 주세요..."
```

교체 후:
```python
def generate_answer(self, state: AgentState) -> str:
    workers_called = state.get("workers_called", [])

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
        count = len(state.get("properties", []))
        parts.append(f"조건에 맞는 매물 {count}개를 찾았습니다.")

    if parts:
        return "\n\n".join(parts)

    return "질문 의도를 조금 더 구체화해 주세요. 매물 추천, 법률 상담, 시세 분석, 안전 분석을 도와드릴 수 있습니다."
```

### 2. `backend-ai/app/api/schemas.py` 전체 교체

```python
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RecentMessage(BaseModel):
    role: str
    content: str


class ChatContext(BaseModel):
    selected_property_id: str | None = Field(default=None, alias="selectedPropertyId")
    recent_messages: list[RecentMessage] = Field(default_factory=list, alias="recentMessages")

    model_config = ConfigDict(populate_by_name=True)


class AgentChatRequest(BaseModel):
    user_id: str = Field(alias="userId")
    session_id: str | None = Field(default=None, alias="sessionId")
    message: str
    context: ChatContext = Field(default_factory=ChatContext)

    model_config = ConfigDict(populate_by_name=True)


class AgentChatResponse(BaseModel):
    workers_called: list[str] = Field(default_factory=list, alias="workersCalled")
    answer: str
    properties: list[dict[str, Any]] = Field(default_factory=list)
    legal_cards: list[dict[str, Any]] = Field(default_factory=list, alias="legalCards")
    analysis_cards: list[dict[str, Any]] = Field(default_factory=list, alias="analysisCards")
    tool_results: dict[str, Any] = Field(default_factory=dict, alias="toolResults")
    next_actions: list[dict[str, Any]] = Field(default_factory=list, alias="nextActions")

    model_config = ConfigDict(populate_by_name=True)
```

### 3. `backend-ai/app/api/routes.py` 수정

`agent_chat` 함수의 return 부분을 수정:

```python
return AgentChatResponse(
    workersCalled=result.get("workers_called", []),
    answer=result["answer"],
    properties=result.get("properties", []),
    legalCards=result.get("legal_cards", []),
    analysisCards=result.get("analysis_cards", []),
    toolResults=result.get("tool_results", {}),
    nextActions=result.get("next_actions", []),
)
```

임포트에서 `Intent` 관련 내용 제거.

STATUS: completed
