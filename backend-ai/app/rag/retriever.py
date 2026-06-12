from typing import Any

from app.clients.supabase_client import SupabaseVectorClient


class LegalRetriever:
    def __init__(self) -> None:
        self.vector_client = SupabaseVectorClient()

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        return self.vector_client.similarity_search_legal_documents(query=query, top_k=top_k)
