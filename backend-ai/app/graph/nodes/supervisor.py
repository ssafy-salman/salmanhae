import logging

from app.clients.llm_client import LLMClient
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


def supervisor(state: AgentState) -> AgentState:
    workers_called = state.get("workers_called", [])
    call_no = len(workers_called) + 1
    logger.info("[supervisor #%d] 호출됨 | workers_called=%s", call_no, workers_called)

    next_worker = LLMClient().decide_next_worker(
        message=state["message"],
        workers_called=workers_called,
    )
    logger.info("[supervisor #%d] → next_worker=%s", call_no, next_worker)

    if next_worker != "FINISH":
        workers_called = [*workers_called, next_worker]
    return {**state, "next_worker": next_worker, "workers_called": workers_called}
