from app.clients.llm_client import LLMClient
from app.graph.state import AgentState


def generate_answer(state: AgentState) -> AgentState:
    client = LLMClient()
    answer = client.generate_answer(state)
    return {**state, "answer": answer}
