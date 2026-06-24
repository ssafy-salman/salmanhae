# Phase 1: State Schema 수정

## Goal
AgentState에서 단일 intent 기반 필드를 제거하고 supervisor 패턴에 필요한 next_worker, workers_called 필드를 추가한다.

## Files
- `backend-ai/app/graph/state.py` — Intent enum 제거, intent 필드 제거, next_worker + workers_called 추가

## Done When
- [ ] `Intent` enum이 `state.py`에서 제거됨
- [ ] `AgentState`에 `intent` 필드가 없음
- [ ] `AgentState`에 `next_worker: NotRequired[str]`가 추가됨
- [ ] `AgentState`에 `workers_called: NotRequired[list[str]]`가 추가됨
- [ ] `cd backend-ai && .venv/bin/python -c "from app.graph.state import AgentState; print('ok')"` 성공

## Architecture Rules
- CLAUDE.md: 모든 비즈니스 로직은 Service 클래스에. State는 데이터 컨테이너 역할만 한다.
- Intent enum은 이 Phase에서만 제거. llm_client.py, schemas.py 등 다른 파일의 Intent 참조는 후속 Phase에서 처리한다.

## Implementation Instructions

현재 `backend-ai/app/graph/state.py` 전체 내용:

```python
from enum import StrEnum
from typing import Any, NotRequired, TypedDict


class Intent(StrEnum):
    PROPERTY_SEARCH = "PROPERTY_SEARCH"
    LEGAL_CONSULT = "LEGAL_CONSULT"
    PRICE_ANALYSIS = "PRICE_ANALYSIS"
    SAFETY_ANALYSIS = "SAFETY_ANALYSIS"
    HUG_CALC = "HUG_CALC"
    GENERAL_CHAT = "GENERAL_CHAT"
    FALLBACK = "FALLBACK"


class AgentState(TypedDict):
    user_id: str
    session_id: str | None
    message: str
    context: dict[str, Any]
    intent: NotRequired[Intent]
    answer: NotRequired[str]
    properties: NotRequired[list[dict[str, Any]]]
    legal_cards: NotRequired[list[dict[str, Any]]]
    analysis_cards: NotRequired[list[dict[str, Any]]]
    tool_results: NotRequired[dict[str, Any]]
    next_actions: NotRequired[list[dict[str, Any]]]
```

위 파일을 아래와 같이 교체한다:

```python
from typing import Any, NotRequired, TypedDict


class AgentState(TypedDict):
    user_id: str
    session_id: str | None
    message: str
    context: dict[str, Any]
    next_worker: NotRequired[str]
    workers_called: NotRequired[list[str]]
    answer: NotRequired[str]
    properties: NotRequired[list[dict[str, Any]]]
    legal_cards: NotRequired[list[dict[str, Any]]]
    analysis_cards: NotRequired[list[dict[str, Any]]]
    tool_results: NotRequired[dict[str, Any]]
    next_actions: NotRequired[list[dict[str, Any]]]
```

변경 후 임포트 확인:
```bash
cd backend-ai && .venv/bin/python -c "from app.graph.state import AgentState; print('ok')"
```

STATUS: completed
