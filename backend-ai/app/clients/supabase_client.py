import json
from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.core.config import get_settings


class SupabaseVectorClient:
    """Client boundary for Supabase PostgreSQL + pgvector legal search."""

    def __init__(
        self,
        connect_timeout_seconds: int | None = None,
        statement_timeout_ms: int | None = None,
    ) -> None:
        settings = get_settings()
        self.database_url = settings.supabase_db_url
        self.connect_timeout_seconds = (
            connect_timeout_seconds
            if connect_timeout_seconds is not None
            else settings.supabase_connect_timeout_seconds
        )
        self.statement_timeout_ms = (
            statement_timeout_ms
            if statement_timeout_ms is not None
            else settings.supabase_statement_timeout_ms
        )

    def similarity_search_legal_documents(
        self,
        query_embedding: list[float],
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        vector_literal = to_pgvector_literal(query_embedding)
        sql = """
            select
                law_name,
                article_no,
                article_title,
                content,
                1 - (embedding <=> %s::vector) as score
            from public.legal_document_chunks
            where embedding is not null
            order by embedding <=> %s::vector
            limit %s
        """
        with psycopg.connect(
            self.database_url,
            row_factory=dict_row,
            connect_timeout=self.connect_timeout_seconds,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "set local statement_timeout = %s",
                    (self.statement_timeout_ms,),
                )
                cursor.execute(sql, (vector_literal, vector_literal, top_k))
                return list(cursor.fetchall())

    def search_properties(self, criteria: dict[str, Any], limit: int = 20) -> list[dict[str, Any]]:
        conditions = ["is_active = true"]
        params: list[Any] = []

        field_map = {
            "sigungu": ("sigungu = %s", "sigungu"),
            "dong": ("dong = %s", "dong"),
            "property_type": ("property_type = %s", "property_type"),
            "transaction_type": ("transaction_type = %s", "transaction_type"),
        }
        range_map = {
            "max_deposit": "deposit <= %s",
            "max_monthly_rent": "monthly_rent <= %s",
            "max_price": "price <= %s",
        }

        for key, (condition, _) in field_map.items():
            if criteria.get(key):
                conditions.append(condition)
                params.append(criteria[key])

        for key, condition in range_map.items():
            if criteria.get(key) is not None:
                conditions.append(condition)
                params.append(criteria[key])

        where_clause = " AND ".join(conditions)
        sql = f"""
            SELECT id, title, building_name, address, property_type, transaction_type,
                   deposit, monthly_rent, price, area_m2, floor, latitude, longitude
            FROM public.properties
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT %s
        """
        params.append(limit)

        with psycopg.connect(
            self.database_url,
            row_factory=dict_row,
            connect_timeout=self.connect_timeout_seconds,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("set local statement_timeout = %s", (self.statement_timeout_ms,))
                cursor.execute(sql, params)
                return list(cursor.fetchall())

    def upsert_legal_document_chunks(self, rows: list[dict[str, Any]]) -> int:
        if not rows:
            return 0

        sql = """
            insert into public.legal_document_chunks as existing (
                law_id,
                law_name,
                article_no,
                article_title,
                effective_date,
                source_name,
                source_url,
                chunk_index,
                content,
                content_hash,
                embedding,
                metadata_json
            )
            values (
                %(law_id)s,
                %(law_name)s,
                %(article_no)s,
                %(article_title)s,
                %(effective_date)s,
                %(source_name)s,
                %(source_url)s,
                %(chunk_index)s,
                %(content)s,
                %(content_hash)s,
                %(embedding)s::vector,
                %(metadata_json)s::jsonb
            )
            on conflict (content_hash) do update set
                law_id = excluded.law_id,
                law_name = excluded.law_name,
                article_no = excluded.article_no,
                article_title = excluded.article_title,
                effective_date = excluded.effective_date,
                source_name = excluded.source_name,
                source_url = excluded.source_url,
                chunk_index = excluded.chunk_index,
                content = excluded.content,
                embedding = excluded.embedding,
                metadata_json = excluded.metadata_json,
                updated_at = now()
            where
                existing.law_id is distinct from excluded.law_id
                or existing.law_name is distinct from excluded.law_name
                or existing.article_no is distinct from excluded.article_no
                or existing.article_title is distinct from excluded.article_title
                or existing.effective_date is distinct from excluded.effective_date
                or existing.source_name is distinct from excluded.source_name
                or existing.source_url is distinct from excluded.source_url
                or existing.chunk_index is distinct from excluded.chunk_index
                or existing.content is distinct from excluded.content
                or existing.embedding is distinct from excluded.embedding
                or existing.metadata_json is distinct from excluded.metadata_json
        """
        params = [legal_chunk_upsert_params(row) for row in rows]
        affected_rows = 0
        with psycopg.connect(
            self.database_url,
            row_factory=dict_row,
            connect_timeout=self.connect_timeout_seconds,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "set local statement_timeout = %s",
                    (self.statement_timeout_ms,),
                )
                for row_params in params:
                    cursor.execute(sql, row_params)
                    affected_rows += max(int(getattr(cursor, "rowcount", 1)), 0)
        return affected_rows


def to_pgvector_literal(embedding: list[float]) -> str:
    if not embedding:
        raise ValueError("query_embedding must not be empty.")
    return "[" + ",".join(f"{float(value):.10g}" for value in embedding) + "]"


def legal_chunk_upsert_params(row: dict[str, Any]) -> dict[str, Any]:
    embedding = row.get("embedding")
    if not isinstance(embedding, list) or not embedding:
        raise ValueError("legal chunk embedding must not be empty.")

    metadata_json = row.get("metadata_json") or {}
    return {
        "law_id": row["law_id"],
        "law_name": row["law_name"],
        "article_no": row["article_no"],
        "article_title": row["article_title"],
        "effective_date": row.get("effective_date"),
        "source_name": row["source_name"],
        "source_url": row["source_url"],
        "chunk_index": row["chunk_index"],
        "content": row["content"],
        "content_hash": row["content_hash"],
        "embedding": to_pgvector_literal(embedding),
        "metadata_json": json.dumps(metadata_json, ensure_ascii=False),
    }
