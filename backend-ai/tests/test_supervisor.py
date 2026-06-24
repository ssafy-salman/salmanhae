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
