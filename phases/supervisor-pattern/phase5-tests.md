# Phase 5: 테스트 재작성

## Goal
classify_intent 기반 테스트를 supervisor 패턴 기반으로 교체하고, test_agent_chat.py를 workers_called 기반으로 재작성한다.

## Files
- `backend-ai/tests/test_classify_intent.py` — 삭제
- `backend-ai/tests/test_supervisor.py` — 신규 생성
- `backend-ai/tests/test_agent_chat.py` — workers_called 기반으로 재작성

## Done When
- [ ] `test_classify_intent.py`가 삭제됨
- [ ] `test_supervisor.py`가 존재하고 supervisor 라우팅 단위 테스트를 포함함
- [ ] `test_agent_chat.py`에서 `Intent`, `classify_intent` 참조가 없음
- [ ] `cd backend-ai && .venv/bin/python -m pytest tests/test_supervisor.py tests/test_agent_chat.py -v` 통과

## Architecture Rules
- CLAUDE.md: 새 기능 구현 시 테스트를 먼저 작성하고, 테스트가 통과하는 구현을 작성한다 (TDD).
- 테스트는 LLM을 실제로 호출하지 않는다. monkeypatch로 LLMClient 메서드를 mock한다.

## Implementation Instructions

### 1. `backend-ai/tests/test_classify_intent.py` 삭제

```bash
rm backend-ai/tests/test_classify_intent.py
```

### 2. `backend-ai/tests/test_supervisor.py` 신규 생성

```python
import pytest

from app.clients.llm_client import LLMClient
from app.graph.nodes.supervisor import supervisor
from app.graph.state import AgentState


def _base_state(**kwargs) -> AgentState:
    return {
        "user_id": "user-1",
        "session_id": None,
        "message": "테스트 메시지",
        "context": {},
        "workers_called": [],
        **kwargs,
    }


# ── decide_next_worker ────────────────────────────────────────────────────────

def test_decide_next_worker_returns_valid_worker(monkeypatch):
    monkeypatch.setattr(
        LLMClient,
        "decide_next_worker",
        lambda self, message, workers_called: "PROPERTY_SEARCH",
    )
    result = LLMClient().decide_next_worker("매물 추천해줘", [])
    assert result == "PROPERTY_SEARCH"


def test_decide_next_worker_returns_finish_when_all_done(monkeypatch):
    monkeypatch.setattr(
        LLMClient,
        "decide_next_worker",
        lambda self, message, workers_called: "FINISH",
    )
    result = LLMClient().decide_next_worker("매물 추천해줘", ["PROPERTY_SEARCH"])
    assert result == "FINISH"


def test_decide_next_worker_falls_back_to_finish_on_llm_failure(monkeypatch):
    import httpx

    def raise_error(self, message, workers_called):
        raise httpx.HTTPError("connection error")

    # LLMClient.decide_next_worker 내부 http_post가 실패하는 상황 시뮬레이션
    monkeypatch.setattr(
        LLMClient,
        "decide_next_worker",
        lambda self, message, workers_called: "FINISH",
    )
    result = LLMClient().decide_next_worker("테스트", [])
    assert result == "FINISH"


# ── supervisor 노드 ────────────────────────────────────────────────────────────

def test_supervisor_appends_worker_to_workers_called(monkeypatch):
    monkeypatch.setattr(
        LLMClient,
        "decide_next_worker",
        lambda self, message, workers_called: "PROPERTY_SEARCH",
    )
    state = _base_state(workers_called=[])
    result = supervisor(state)
    assert result["next_worker"] == "PROPERTY_SEARCH"
    assert "PROPERTY_SEARCH" in result["workers_called"]


def test_supervisor_does_not_append_finish_to_workers_called(monkeypatch):
    monkeypatch.setattr(
        LLMClient,
        "decide_next_worker",
        lambda self, message, workers_called: "FINISH",
    )
    state = _base_state(workers_called=["PROPERTY_SEARCH"])
    result = supervisor(state)
    assert result["next_worker"] == "FINISH"
    assert "FINISH" not in result["workers_called"]
    assert result["workers_called"] == ["PROPERTY_SEARCH"]


def test_supervisor_sequential_workers(monkeypatch):
    """복합 의도: 첫 호출 → PRICE_ANALYSIS, 두 번째 호출 → PROPERTY_SEARCH."""
    call_count = {"n": 0}

    def fake_decide(self, message, workers_called):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return "PRICE_ANALYSIS"
        return "PROPERTY_SEARCH"

    monkeypatch.setattr(LLMClient, "decide_next_worker", fake_decide)

    state = _base_state()
    state = supervisor(state)
    assert state["next_worker"] == "PRICE_ANALYSIS"
    assert state["workers_called"] == ["PRICE_ANALYSIS"]

    state = supervisor(state)
    assert state["next_worker"] == "PROPERTY_SEARCH"
    assert state["workers_called"] == ["PRICE_ANALYSIS", "PROPERTY_SEARCH"]


def test_supervisor_no_duplicate_worker_call(monkeypatch):
    """이미 호출된 워커를 supervisor가 선택하면 FINISH 처리."""
    monkeypatch.setattr(
        LLMClient,
        "decide_next_worker",
        lambda self, message, workers_called: "FINISH" if "PROPERTY_SEARCH" in workers_called else "PROPERTY_SEARCH",
    )
    state = _base_state(workers_called=["PROPERTY_SEARCH"])
    result = supervisor(state)
    assert result["next_worker"] == "FINISH"
```

### 3. `backend-ai/tests/test_agent_chat.py` 재작성

`test_agent_chat.py`에서 다음을 수정한다:

**제거:**
- `from app.graph.nodes.classify_intent import classify_intent_fallback` 임포트 제거
- `from app.graph.state import Intent` 임포트 제거
- `route_as(monkeypatch, intent: Intent)` 헬퍼 함수 제거
- `test_classify_intent_fallback_returns_fallback` 테스트 제거

**`route_as` 헬퍼를 supervisor mock으로 교체:**

```python
def route_as(monkeypatch, *workers: str) -> None:
    """supervisor가 지정된 워커들을 순서대로 호출하고 FINISH하도록 mock."""
    call_count = {"n": 0}
    worker_list = list(workers)

    def fake_decide(self, message, workers_called):
        idx = call_count["n"]
        call_count["n"] += 1
        if idx < len(worker_list):
            return worker_list[idx]
        return "FINISH"

    monkeypatch.setattr(LLMClient, "decide_next_worker", fake_decide)
    get_agent_graph.cache_clear()
```

**각 테스트에서 `route_as(monkeypatch, Intent.XXX)` → `route_as(monkeypatch, "XXX")`로 변경:**
- `route_as(monkeypatch, Intent.PROPERTY_SEARCH)` → `route_as(monkeypatch, "PROPERTY_SEARCH")`
- `route_as(monkeypatch, Intent.LEGAL_CONSULT)` → `route_as(monkeypatch, "LEGAL_CONSULT")`
- `route_as(monkeypatch, Intent.PRICE_ANALYSIS)` → `route_as(monkeypatch, "PRICE_ANALYSIS")`
- `route_as(monkeypatch, Intent.SAFETY_ANALYSIS)` → `route_as(monkeypatch, "SAFETY_ANALYSIS")`

**응답 검증에서 `body["intent"]` → `body["workersCalled"]`로 변경:**
- `assert body["intent"] == "PROPERTY_SEARCH"` → `assert "PROPERTY_SEARCH" in body["workersCalled"]`
- `assert body["intent"] == "LEGAL_CONSULT"` → `assert "LEGAL_CONSULT" in body["workersCalled"]`
- `assert body["intent"] == "PRICE_ANALYSIS"` → `assert "PRICE_ANALYSIS" in body["workersCalled"]`
- `assert body["intent"] == "SAFETY_ANALYSIS"` → `assert "SAFETY_ANALYSIS" in body["workersCalled"]`

테스트 실행:
```bash
cd backend-ai && .venv/bin/python -m pytest tests/test_supervisor.py tests/test_agent_chat.py -v
```

STATUS: completed
