from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.core.config import get_settings


class SupabaseVectorClient:
    """Client boundary for Supabase PostgreSQL + pgvector legal search."""

    def __init__(self) -> None:
        self.database_url = get_settings().supabase_db_url

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
        with psycopg.connect(self.database_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (vector_literal, vector_literal, top_k))
                return list(cursor.fetchall())


def to_pgvector_literal(embedding: list[float]) -> str:
    if not embedding:
        raise ValueError("query_embedding must not be empty.")
    return "[" + ",".join(f"{float(value):.10g}" for value in embedding) + "]"
