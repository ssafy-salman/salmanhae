from typing import Any

from app.core.config import get_settings


class SupabaseVectorClient:
    """Client boundary for Supabase PostgreSQL + pgvector legal search."""

    def __init__(self) -> None:
        self.database_url = get_settings().supabase_db_url

    def similarity_search_legal_documents(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        return [
            {
                "title": "주택임대차보호법 - 대항력",
                "source": "legal-stub",
                "content": "임차인은 주택의 인도와 주민등록을 마친 때에는 그 다음 날부터 제3자에 대하여 효력이 생깁니다.",
                "score": 0.91,
            },
            {
                "title": "주택임대차보호법 - 확정일자",
                "source": "legal-stub",
                "content": "확정일자를 갖춘 임차인은 경매 또는 공매 시 후순위권리자보다 우선하여 보증금을 변제받을 수 있습니다.",
                "score": 0.86,
            },
        ][:top_k]
