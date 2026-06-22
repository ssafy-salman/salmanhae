from typing import Any, Protocol

from app.clients.embedding_client import EmbeddingClient
from app.clients.supabase_client import SupabaseVectorClient


class EmbeddingClientProtocol(Protocol):
    def embed_query(self, query: str) -> list[float]:
        ...


class VectorClientProtocol(Protocol):
    def similarity_search_legal_documents(
        self,
        query_embedding: list[float],
        top_k: int,
    ) -> list[dict[str, Any]]:
        ...


class LegalRetriever:
    def __init__(
        self,
        embedding_client: EmbeddingClientProtocol | None = None,
        vector_client: VectorClientProtocol | None = None,
        max_top_k: int = 5,
    ) -> None:
        self.embedding_client = embedding_client or EmbeddingClient()
        self.vector_client = vector_client or SupabaseVectorClient()
        self.max_top_k = max_top_k

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        normalized_query = query.strip()
        if not normalized_query:
            return []

        safe_top_k = min(max(top_k, 1), self.max_top_k)
        query_embedding = self.embedding_client.embed_query(normalized_query)
        rows = self.vector_client.similarity_search_legal_documents(
            query_embedding=query_embedding,
            top_k=safe_top_k,
        )
        return [normalize_legal_card(row) for row in rows]


def normalize_legal_card(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "lawName": row.get("lawName") or row["law_name"],
        "articleNo": row.get("articleNo") or row["article_no"],
        "title": row.get("title") or row["article_title"],
        "content": row["content"],
        "score": float(row["score"]),
    }
