import json

import httpx

from app.clients.llm_client import LLMClient
from app.graph.nodes.supervisor import supervisor
from app.graph.state import AgentState


def _mock_llm_response(next_worker: str) -> httpx.Response:
    payload = json.dumps({
        "choices": [{"message": {"content": json.dumps({"next_worker": next_worker, "reasoning": "test"})}}]
    })
    request = httpx.Request("POST", "http://test/chat/completions")
    return httpx.Response(200, content=payload.encode(), headers={"content-type": "application/json"}, request=request)


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

def test_decide_next_worker_returns_valid_worker():
    """LLM이 유효한 워커를 반환하면 그대로 반환한다."""
    client = LLMClient(
        api_key="test", model="test", base_url="http://test",
        http_post=lambda *a, **kw: _mock_llm_response("PROPERTY_SEARCH"),
    )
    assert client.decide_next_worker("매물 추천해줘", []) == "PROPERTY_SEARCH"


def test_decide_next_worker_returns_finish_for_already_called_worker():
    """LLM이 이미 호출된 워커를 반환하면 FINISH를 반환한다."""
    client = LLMClient(
        api_key="test", model="test", base_url="http://test",
        http_post=lambda *a, **kw: _mock_llm_response("PROPERTY_SEARCH"),
    )
    assert client.decide_next_worker("매물 추천해줘", ["PROPERTY_SEARCH"]) == "FINISH"


def test_decide_next_worker_returns_finish_for_invalid_worker():
    """LLM이 유효하지 않은 워커명을 반환하면 FINISH를 반환한다."""
    client = LLMClient(
        api_key="test", model="test", base_url="http://test",
        http_post=lambda *a, **kw: _mock_llm_response("INVALID_WORKER"),
    )
    assert client.decide_next_worker("테스트", []) == "FINISH"


def test_decide_next_worker_falls_back_to_property_search_on_first_call_failure():
    """첫 호출(workers_called 빈 상태)에서 LLM 장애 시 PROPERTY_SEARCH를 반환한다."""
    def raise_error(*a, **kw):
        raise httpx.ConnectError("connection failed")

    client = LLMClient(api_key="test", model="test", base_url="http://test", http_post=raise_error)
    assert client.decide_next_worker("테스트", []) == "PROPERTY_SEARCH"


def test_decide_next_worker_falls_back_to_finish_on_failure_after_workers():
    """워커가 이미 실행된 후 LLM 장애 시 FINISH를 반환한다."""
    def raise_error(*a, **kw):
        raise httpx.ConnectError("connection failed")

    client = LLMClient(api_key="test", model="test", base_url="http://test", http_post=raise_error)
    assert client.decide_next_worker("테스트", ["PROPERTY_SEARCH"]) == "FINISH"


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
