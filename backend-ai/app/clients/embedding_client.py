from typing import Any

import httpx

from app.core.config import get_settings


class EmbeddingClient:
    """HTTP boundary for query embeddings."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.embedding_api_key
        self.base_url = (base_url or settings.embedding_base_url).rstrip("/")
        self.model = model or settings.embedding_model
        self.timeout_seconds = timeout_seconds

    def embed_query(self, query: str) -> list[float]:
        if not query.strip():
            raise ValueError("query must not be blank.")
        if not self.api_key or not self.model:
            raise RuntimeError("Embedding client is not configured.")

        response = httpx.post(
            f"{self.base_url}/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "input": query},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        data = payload.get("data")
        if not isinstance(data, list) or not data or not isinstance(data[0], dict):
            raise RuntimeError("Embedding response did not include data.")

        embedding = data[0].get("embedding")
        if not isinstance(embedding, list):
            raise RuntimeError("Embedding response did not include an embedding vector.")
        return [float(value) for value in embedding]
