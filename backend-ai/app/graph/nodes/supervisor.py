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
