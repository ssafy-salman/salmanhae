import json

import pytest

from app.clients import supabase_client as supabase_module
from app.clients.supabase_client import SupabaseVectorClient
from scripts.ingest_legal_docs import (
    embed_legal_chunks,
    main,
    write_legal_chunks,
)


class FakeEmbeddingClient:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def embed_query(self, query: str) -> list[float]:
        self.queries.append(query)
        return [float(len(self.queries)), 0.5]


class FakeVectorClient:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def upsert_legal_document_chunks(self, rows: list[dict]) -> int:
        self.rows.extend(rows)
        return len(rows)


def write_source(tmp_path, documents):
    source_path = tmp_path / "legal-documents.json"
    source_path.write_text(json.dumps(documents), encoding="utf-8")
    return source_path


def sample_rows() -> list[dict]:
    return [
        {
            "law_id": "housing-lease-protection-act",
            "law_name": "Housing Lease Protection Act",
            "article_no": "Article 3-2",
            "article_title": "Recovery of Deposit",
            "effective_date": "2025-01-01",
            "source_name": "law.go.kr",
            "source_url": "https://www.law.go.kr",
            "chunk_index": 0,
            "content": "A tenant may recover the deposit before junior creditors.",
            "content_hash": "a" * 64,
            "embedding": None,
            "metadata_json": {"sourceUrl": "https://www.law.go.kr"},
        }
    ]


def test_embed_legal_chunks_uses_embedding_client_without_mutating_source() -> None:
    rows = sample_rows()
    embedding_client = FakeEmbeddingClient()

    embedded_rows = embed_legal_chunks(rows, embedding_client)

    assert embedding_client.queries == [
        "A tenant may recover the deposit before junior creditors."
    ]
    assert rows[0]["embedding"] is None
    assert embedded_rows[0]["embedding"] == [1.0, 0.5]
    assert embedded_rows[0]["content_hash"] == rows[0]["content_hash"]


def test_write_legal_chunks_embeds_then_upserts_rows() -> None:
    embedding_client = FakeEmbeddingClient()
    vector_client = FakeVectorClient()

    summary = write_legal_chunks(sample_rows(), embedding_client, vector_client)

    assert summary == {"chunks": 1, "upserted": 1}
    assert embedding_client.queries == [
        "A tenant may recover the deposit before junior creditors."
    ]
    assert vector_client.rows[0]["embedding"] == [1.0, 0.5]


def test_main_requires_explicit_mode_for_database_writes(tmp_path) -> None:
    source_path = write_source(tmp_path, [])

    with pytest.raises(SystemExit):
        main([str(source_path)])


def test_write_mode_outputs_summary_with_injected_clients(tmp_path, capsys) -> None:
    source_path = write_source(
        tmp_path,
        [
            {
                "lawId": "housing-lease-protection-act",
                "lawName": "Housing Lease Protection Act",
                "articleNo": "Article 3-2",
                "title": "Recovery of Deposit",
                "content": "A tenant may recover the deposit before junior creditors.",
                "sourceUrl": "https://www.law.go.kr",
                "effectiveDate": "2025-01-01",
            }
        ],
    )
    embedding_client = FakeEmbeddingClient()
    vector_client = FakeVectorClient()

    exit_code = main(
        ["--write", "--chunk-size", "200", str(source_path)],
        embedding_client=embedding_client,
        vector_client=vector_client,
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Legal ingestion write" in output
    assert "documents=1" in output
    assert "chunks=1" in output
    assert "upserted=1" in output
    assert len(vector_client.rows) == 1


def test_supabase_vector_client_upserts_legal_chunks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: dict[str, object] = {}

    class FakeCursor:
        rowcount = 1

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback) -> None:
            return None

        def execute(self, sql, params=None) -> None:
            calls.setdefault("executes", []).append((sql, params))

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

    upserted = client.upsert_legal_document_chunks(
        [{**sample_rows()[0], "embedding": [0.1, 0.2]}]
    )

    executes = calls["executes"]
    assert upserted == 1
    assert executes[0] == ("set local statement_timeout = 3000", None)
    assert "on conflict (content_hash)" in executes[1][0]
    assert "where" in executes[1][0]
    assert "existing.content is distinct from excluded.content" in executes[1][0]
    assert executes[1][1]["embedding"] == "[0.1,0.2]"
    assert executes[1][1]["metadata_json"] == '{"sourceUrl": "https://www.law.go.kr"}'


def test_dry_run_mode_returns_success(tmp_path) -> None:
    source_path = write_source(
        tmp_path,
        [
            {
                "lawId": "housing-lease-protection-act",
                "lawName": "Housing Lease Protection Act",
                "articleNo": "Article 3-2",
                "title": "Recovery of Deposit",
                "content": "A tenant may recover the deposit before junior creditors.",
                "sourceUrl": "https://www.law.go.kr",
            }
        ],
    )

    exit_code = main(["--dry-run", str(source_path)])

    assert exit_code == 0
