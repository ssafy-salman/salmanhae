import json
import math
import re
from typing import Any

import httpx
import psycopg
from psycopg.rows import dict_row

from app.core.config import get_settings


REST_PAGE_SIZE = 1000


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
        try:
            return self._similarity_search_legal_documents_pgvector(
                query_embedding=query_embedding,
                top_k=top_k,
            )
        except psycopg.OperationalError:
            settings = get_settings()
            if settings.app_env.lower() in {"prod", "production"}:
                raise
            return self._similarity_search_legal_documents_rest(
                query_embedding=query_embedding,
                top_k=top_k,
            )

    def _similarity_search_legal_documents_pgvector(
        self,
        query_embedding: list[float],
        top_k: int,
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
                cursor.execute(f"set local statement_timeout = {int(self.statement_timeout_ms)}")
                # IVFFlat 인덱스가 lists=100으로 설정돼 있으나 데이터 수가 적을 때
                # 기본 probes=1이면 대부분의 클러스터를 건너뛰어 결과가 0개가 됨.
                # probes를 lists 값과 동일하게 설정해 전체 인덱스를 탐색하도록 한다.
                cursor.execute("set local ivfflat.probes = 100")
                cursor.execute(sql, (vector_literal, vector_literal, top_k))
                return list(cursor.fetchall())

    def get_regional_price_stats(
        self,
        sigungu: str | None = None,
        dong: str | None = None,
        property_type: str | None = None,
        transaction_type: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: list[Any] = []

        if sigungu:
            conditions.append("sigungu = %s")
            params.append(sigungu)
        if dong:
            conditions.append("dong = %s")
            params.append(dong)
        if property_type:
            conditions.append("property_type = %s")
            params.append(property_type)
        if transaction_type:
            conditions.append("transaction_type = %s")
            params.append(transaction_type)

        if not conditions:
            return []

        where_clause = " AND ".join(conditions)
        sql = f"""
            SELECT region_level, region_code, sigungu, dong,
                   property_type, transaction_type,
                   avg_deposit, median_deposit,
                   avg_monthly_rent, median_monthly_rent,
                   avg_price, median_price,
                   transaction_count, sample_from_ym, sample_to_ym
            FROM public.region_price_stat
            WHERE {where_clause}
            ORDER BY transaction_count DESC NULLS LAST
            LIMIT %s
        """
        params.append(limit)

        with psycopg.connect(
            self.database_url,
            row_factory=dict_row,
            connect_timeout=self.connect_timeout_seconds,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"set local statement_timeout = {int(self.statement_timeout_ms)}")
                cursor.execute(sql, params)
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

        sort_by = criteria.get("sort_by")
        if sort_by == "price_asc":
            order_clause = """
                CASE transaction_type
                    WHEN 'SALE' THEN price
                    WHEN 'JEONSE' THEN deposit
                    WHEN 'MONTHLY_RENT' THEN monthly_rent
                    ELSE COALESCE(price, deposit, monthly_rent)
                END ASC NULLS LAST
            """
        else:
            order_clause = "created_at DESC"

        where_clause = " AND ".join(conditions)
        sql = f"""
            SELECT id, title, building_name, address, property_type, transaction_type,
                   deposit, monthly_rent, price, area_m2, floor, latitude, longitude
            FROM public.properties
            WHERE {where_clause}
            ORDER BY {order_clause}
            LIMIT %s
        """
        params.append(limit)

        with psycopg.connect(
            self.database_url,
            row_factory=dict_row,
            connect_timeout=self.connect_timeout_seconds,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"set local statement_timeout = {int(self.statement_timeout_ms)}")
                cursor.execute(sql, params)
                return list(cursor.fetchall())

    def _similarity_search_legal_documents_rest(
        self,
        query_embedding: list[float],
        top_k: int,
    ) -> list[dict[str, Any]]:
        settings = get_settings()
        project_ref = supabase_project_ref(settings.supabase_db_url)
        if not project_ref or not settings.supabase_service_role_key:
            raise RuntimeError("Supabase REST fallback is not configured.")

        url = f"https://{project_ref}.supabase.co/rest/v1/legal_document_chunks"
        headers = {
            "apikey": settings.supabase_service_role_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
        }
        rows: list[dict[str, Any]] = []
        offset = 0
        while True:
            response = httpx.get(
                url,
                headers=headers,
                params={
                    "select": "law_name,article_no,article_title,content,embedding",
                    "embedding": "not.is.null",
                    "limit": str(REST_PAGE_SIZE),
                    "offset": str(offset),
                },
                timeout=self.connect_timeout_seconds + 10,
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list) or not payload:
                break

            for row in payload:
                if not isinstance(row, dict):
                    continue
                embedding = parse_pgvector_value(row.get("embedding"))
                if not embedding:
                    continue
                rows.append(
                    {
                        "law_name": row["law_name"],
                        "article_no": row["article_no"],
                        "article_title": row["article_title"],
                        "content": row["content"],
                        "score": cosine_similarity(query_embedding, embedding),
                    }
                )
            if len(payload) < REST_PAGE_SIZE:
                break
            offset += REST_PAGE_SIZE
        return sorted(rows, key=lambda item: item["score"], reverse=True)[:top_k]

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
                cursor.execute(f"set local statement_timeout = {int(self.statement_timeout_ms)}")
                for row_params in params:
                    cursor.execute(sql, row_params)
                    affected_rows += max(int(getattr(cursor, "rowcount", 1)), 0)
        return affected_rows


def to_pgvector_literal(embedding: list[float]) -> str:
    if not embedding:
        raise ValueError("query_embedding must not be empty.")
    return "[" + ",".join(f"{float(value):.10g}" for value in embedding) + "]"


def supabase_project_ref(database_url: str) -> str | None:
    match = re.search(r"postgres(?:ql)?://([^:]+):[^@]+@", database_url)
    if not match:
        return None
    username = match.group(1)
    if "." not in username:
        return None
    return username.split(".", 1)[1]


def parse_pgvector_value(value: Any) -> list[float]:
    if isinstance(value, list):
        return [parsed for item in value if (parsed := parse_float_value(item)) is not None]
    if not isinstance(value, str):
        return []
    stripped = value.strip()
    if not stripped.startswith("[") or not stripped.endswith("]"):
        return []
    body = stripped[1:-1].strip()
    if not body:
        return []
    return [
        parsed
        for item in body.split(",")
        if item.strip()
        if (parsed := parse_float_value(item.strip())) is not None
    ]


def parse_float_value(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


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
