# Phase 3: Builder 재구성 + classify_intent 삭제

## Goal
LangGraph 그래프를 supervisor 순환 패턴으로 재구성하고 classify_intent 노드를 제거한다.

## Files
- `backend-ai/app/graph/builder.py` — supervisor 순환 그래프로 교체
- `backend-ai/app/graph/nodes/classify_intent.py` — 삭제

## Done When
- [ ] `builder.py`에 classify_intent, route_by_intent, fallback 관련 코드가 없음
- [ ] `builder.py`에 supervisor 노드가 START와 연결됨
- [ ] 각 워커(property_search, legal_rag, price_analysis, safety_analysis) 완료 후 supervisor로 복귀하는 엣지가 있음
- [ ] supervisor가 FINISH 결정 시 generate_answer로 진행하는 조건부 엣지가 있음
- [ ] `classify_intent.py`가 삭제됨
- [ ] `cd backend-ai && .venv/bin/python -c "from app.graph.builder import build_agent_graph; g = build_agent_graph(); print('ok')"` 성공

## Architecture Rules
- CLAUDE.md: AI 에이전트(LangGraph)는 backend-ai 서비스에만 존재한다.
- CLAUDE.md: 비즈니스 로직은 Service/Client 클래스에. Builder는 그래프 구조 정의만 한다.

## Implementation Instructions

### 1. `backend-ai/app/graph/nodes/classify_intent.py` 삭제

```bash
rm backend-ai/app/graph/nodes/classify_intent.py
```

### 2. `backend-ai/app/graph/builder.py` 전체 교체

현재 파일을 아래 내용으로 완전히 교체한다:

```python
from langgraph.graph import END, START, StateGraph

from app.graph.nodes.generate_answer import generate_answer
from app.graph.nodes.legal_rag import legal_rag
from app.graph.nodes.price_analysis import price_analysis
from app.graph.nodes.property_search import property_search
from app.graph.nodes.safety_analysis import safety_analysis
from app.graph.nodes.supervisor import supervisor
from app.graph.state import AgentState


def route_after_supervisor(state: AgentState) -> str:
    mapping = {
        "PROPERTY_SEARCH": "property_search",
        "LEGAL_CONSULT": "legal_rag",
        "PRICE_ANALYSIS": "price_analysis",
        "SAFETY_ANALYSIS": "safety_analysis",
        "FINISH": "generate_answer",
    }
    return mapping.get(state.get("next_worker", "FINISH"), "generate_answer")


def build_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor)
    workflow.add_node("property_search", property_search)
    workflow.add_node("legal_rag", legal_rag)
    workflow.add_node("price_analysis", price_analysis)
    workflow.add_node("safety_analysis", safety_analysis)
    workflow.add_node("generate_answer", generate_answer)

    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "property_search": "property_search",
            "legal_rag": "legal_rag",
            "price_analysis": "price_analysis",
            "safety_analysis": "safety_analysis",
            "generate_answer": "generate_answer",
        },
    )

    for node in ["property_search", "legal_rag", "price_analysis", "safety_analysis"]:
        workflow.add_edge(node, "supervisor")

    workflow.add_edge("generate_answer", END)
    return workflow.compile()
```

변경 후 그래프 빌드 확인:
```bash
cd backend-ai && .venv/bin/python -c "from app.graph.builder import build_agent_graph; g = build_agent_graph(); print('ok')"
```

STATUS: completed
