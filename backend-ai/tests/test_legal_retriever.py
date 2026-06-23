import os

import pytest

from app.clients import supabase_client as supabase_module
from app.clients.supabase_client import SupabaseVectorClient, parse_pgvector_value
from app.graph.nodes import legal_rag as legal_rag_module
from app.graph.state import Intent
from app.rag.retriever import LegalRetriever


class FakeEmbeddingClient:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def embed_query(self, query: str) -> list[float]:
        self.queries.append(query)
        return [0.1, 0.2, 0.3]


class FakeVectorClient:
    def __init__(self, rows):
        self.rows = rows
        self.calls: list[dict] = []

    def similarity_search_legal_documents(
        self,
        query_embedding: list[float],
        top_k: int,
    ) -> list[dict]:
        self.calls.append({"query_embedding": query_embedding, "top_k": top_k})
        return self.rows[:top_k]


def test_legal_retriever_normalizes_pgvector_rows() -> None:
    embedding_client = FakeEmbeddingClient()
    vector_client = FakeVectorClient(
        [
            {
                "law_name": "주택임대차보호법",
                "article_no": "제3조의2",
                "article_title": "보증금의 회수",
                "content": "임차인은 보증금을 우선변제받을 권리가 있다.",
                "score": 0.91,
            }
        ]
    )
    retriever = LegalRetriever(
        embedding_client=embedding_client,
        vector_client=vector_client,
    )

    cards = retriever.retrieve("보증금은 어떻게 돌려받나요?", top_k=3)

    assert embedding_client.queries == ["보증금은 어떻게 돌려받나요?"]
    assert vector_client.calls == [{"query_embedding": [0.1, 0.2, 0.3], "top_k": 3}]
    assert cards == [
        {
            "lawName": "주택임대차보호법",
            "articleNo": "제3조의2",
            "title": "보증금의 회수",
            "content": "임차인은 보증금을 우선변제받을 권리가 있다.",
            "score": 0.91,
        }
    ]


def test_legal_retriever_returns_empty_for_blank_query_without_external_calls() -> None:
    embedding_client = FakeEmbeddingClient()
    vector_client = FakeVectorClient([])
    retriever = LegalRetriever(
        embedding_client=embedding_client,
        vector_client=vector_client,
    )

    assert retriever.retrieve("   ") == []
    assert embedding_client.queries == []
    assert vector_client.calls == []


def test_legal_retriever_clamps_top_k() -> None:
    embedding_client = FakeEmbeddingClient()
    vector_client = FakeVectorClient([])
    retriever = LegalRetriever(
        embedding_client=embedding_client,
        vector_client=vector_client,
        max_top_k=5,
    )

    retriever.retrieve("대항력", top_k=99)

    assert vector_client.calls[0]["top_k"] == 5


def test_legal_rag_node_records_tool_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeRetriever:
        def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
            return [
                {
                    "lawName": "주택임대차보호법",
                    "articleNo": "제3조",
                    "title": "대항력",
                    "content": "임차인은 대항력을 취득한다.",
                    "score": 0.88,
                }
            ]

    monkeypatch.setattr(legal_rag_module, "LegalRetriever", FakeRetriever)

    result = legal_rag_module.legal_rag(
        {
            "user_id": "user-1",
            "session_id": None,
            "message": "대항력이 뭐예요?",
            "context": {},
            "intent": Intent.LEGAL_CONSULT,
        }
    )

    assert len(result["legal_cards"]) == 1
    assert result["tool_results"]["legalRag"] == {
        "topK": 1,
        "source": "supabase-pgvector",
    }


def test_supabase_vector_client_sets_connection_and_statement_timeouts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: dict[str, object] = {}

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback) -> None:
            return None

        def execute(self, sql, params) -> None:
            calls.setdefault("executes", []).append((sql, params))

        def fetchall(self) -> list[dict]:
            return []

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback) -> None:
            return None

        def cursor(self) -> FakeCursor:
            return FakeCursor()

    def fake_connect(database_url, **kwargs):
        calls["database_url"] = database_url
        calls["connect_kwargs"] = kwargs
        return FakeConnection()

    monkeypatch.setattr(supabase_module.psycopg, "connect", fake_connect)
    client = SupabaseVectorClient(
        connect_timeout_seconds=7,
        statement_timeout_ms=3000,
    )

    client.similarity_search_legal_documents([0.1, 0.2], top_k=2)

    assert calls["connect_kwargs"]["connect_timeout"] == 7
    assert len(calls.get("executes", [])) >= 1
    assert calls["executes"][0] == ("set local statement_timeout = %s", (3000,))


def test_parse_pgvector_value_supports_postgrest_vector_strings() -> None:
    assert parse_pgvector_value("[0.1,0.2,-0.3]") == [0.1, 0.2, -0.3]
    assert parse_pgvector_value([1, "2.5"]) == [1.0, 2.5]
    assert parse_pgvector_value("[0.1,broken,0.3]") == [0.1, 0.3]


def test_supabase_vector_client_falls_back_to_rest_when_pg_is_unreachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TEST_SUPABASE_DB_URL", "unused-test-db-url")
    monkeypatch.setenv("TEST_SUPABASE_SERVICE_ROLE_KEY", "unused-test-service-role-key")

    class FakeSettings:
        supabase_db_url = os.environ["TEST_SUPABASE_DB_URL"]
        supabase_connect_timeout_seconds = 1
        supabase_statement_timeout_ms = 1000
        supabase_service_role_key = os.environ["TEST_SUPABASE_SERVICE_ROLE_KEY"]

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> list[dict]:
            return [
                {
                    "law_name": "주택임대차보호법",
                    "article_no": "제3조의2",
                    "article_title": "보증금의 회수",
                    "content": "임차인은 보증금을 우선변제 받을 권리가 있다.",
                    "embedding": "[1,0]",
                },
                {
                    "law_name": "전세사기피해자 지원 및 주거안정에 관한 특별법",
                    "article_no": "제1조",
                    "article_title": "목적",
                    "content": "전세사기피해자를 지원한다.",
                    "embedding": "[0,1]",
                },
            ]

    calls: dict[str, object] = {}

    def fake_connect(*args, **kwargs):
        raise supabase_module.psycopg.OperationalError("blocked")

    def fake_get(url, **kwargs):
        calls["url"] = url
        calls["kwargs"] = kwargs
        return FakeResponse()

    monkeypatch.setattr(supabase_module, "get_settings", lambda: FakeSettings())
    monkeypatch.setattr(supabase_module, "supabase_project_ref", lambda database_url: "project-ref")
    monkeypatch.setattr(supabase_module.psycopg, "connect", fake_connect)
    monkeypatch.setattr(supabase_module.httpx, "get", fake_get)

    client = SupabaseVectorClient()
    rows = client.similarity_search_legal_documents([1, 0], top_k=1)

    assert rows == [
        {
            "law_name": "주택임대차보호법",
            "article_no": "제3조의2",
            "article_title": "보증금의 회수",
            "content": "임차인은 보증금을 우선변제 받을 권리가 있다.",
            "score": 1.0,
        }
    ]
    assert calls["url"].startswith("https://project-ref.supabase.co/rest/v1/legal_document_chunks")
