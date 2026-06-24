# Phase 2: Supervisor 노드 구현

## Goal
LLM이 workers_called를 보고 다음 워커를 동적으로 결정하는 supervisor 노드와 LLMClient 메서드를 구현한다.

## Files
- `backend-ai/app/graph/nodes/supervisor.py` — 신규 생성
- `backend-ai/app/clients/llm_client.py` — SUPERVISOR_PROMPT + decide_next_worker() 추가

## Done When
- [ ] `supervisor.py`가 존재하고 `supervisor(state)` 함수를 export함
- [ ] `LLMClient.decide_next_worker(message, workers_called)` 메서드가 존재함
- [ ] workers_called에 이미 있는 워커는 다시 선택하지 않음
- [ ] LLM 호출 실패 시 "FINISH"를 반환하는 안전 폴백이 있음
- [ ] `cd backend-ai && .venv/bin/python -c "from app.graph.nodes.supervisor import supervisor; print('ok')"` 성공

## Architecture Rules
- CLAUDE.md: AI 에이전트(LangGraph)는 backend-ai 서비스에만 존재한다.
- CLAUDE.md: API 키는 환경변수로 관리. 코드에 하드코딩 금지.
- CLAUDE.md: 비즈니스 로직은 Service/Client 클래스에. 노드 함수는 위임만 한다.

## Implementation Instructions

### 1. `backend-ai/app/clients/llm_client.py`에 추가할 내용

파일 상단 기존 import 아래에 SUPERVISOR_PROMPT 추가:

```python
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
```

`LLMClient` 클래스에 메서드 추가:

```python
def decide_next_worker(self, message: str, workers_called: list[str]) -> str:
    """supervisor 역할: 다음에 호출할 워커 또는 FINISH를 결정한다."""
    prompt = SUPERVISOR_PROMPT.format(
        message=message,
        workers_called=", ".join(workers_called) if workers_called else "없음",
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
                "max_completion_tokens": 128,
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        text = extract_chat_completion_text(response.json()) or "{}"
        parsed = json.loads(text)
        next_worker = parsed.get("next_worker", "FINISH")
        valid = {"PROPERTY_SEARCH", "LEGAL_CONSULT", "PRICE_ANALYSIS", "SAFETY_ANALYSIS", "GENERAL_CHAT", "FINISH"}
        if next_worker not in valid:
            return "FINISH"
        # 이미 호출된 워커를 다시 선택한 경우 FINISH로 안전 처리
        if next_worker in workers_called:
            return "FINISH"
        return next_worker
    except (httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        if not workers_called:
            return "PROPERTY_SEARCH"
        return "FINISH"
```

### 2. `backend-ai/app/graph/nodes/supervisor.py` 신규 생성

```python
from app.clients.llm_client import LLMClient
from app.graph.state import AgentState


def supervisor(state: AgentState) -> AgentState:
    workers_called = state.get("workers_called", [])
    next_worker = LLMClient().decide_next_worker(
        message=state["message"],
        workers_called=workers_called,
    )
    if next_worker != "FINISH":
        workers_called = [*workers_called, next_worker]
    return {**state, "next_worker": next_worker, "workers_called": workers_called}
```

STATUS: completed
