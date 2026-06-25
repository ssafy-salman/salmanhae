import pytest

from app.clients import supabase_client as supabase_module
from app.clients.llm_client import LLMClient
from app.clients.supabase_client import SupabaseVectorClient


def test_search_properties_can_order_by_safety_score(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: dict[str, object] = {"executes": []}

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback) -> None:
            return None

        def execute(self, sql, params=None) -> None:
            calls["executes"].append((sql, params))

        def fetchall(self) -> list[dict]:
            return [
                {
                    "id": 1,
                    "title": "safe home",
                    "building_name": "green villa",
                    "address": "Seoul",
                    "property_type": "ONE_ROOM",
                    "transaction_type": "MONTHLY_RENT",
                    "deposit": 10000000,
                    "monthly_rent": 500000,
                    "price": None,
                    "area_m2": 22.5,
                    "floor": 3,
                    "latitude": 37.47,
                    "longitude": 126.93,
                    "safety_score": 91,
                    "cctv_count_300m": 12,
                    "bell_count_300m": 3,
                    "light_count_300m": 21,
                    "police_count_500m": 1,
                }
            ]

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback) -> None:
            return None

        def cursor(self) -> FakeCursor:
            return FakeCursor()

    monkeypatch.setattr(
        supabase_module.psycopg,
        "connect",
        lambda *args, **kwargs: FakeConnection(),
    )

    client = SupabaseVectorClient()
    rows = client.search_properties(
        {"sort_by": "safety_desc", "min_safety_score": 70},
        limit=5,
    )

    query_sql, query_params = calls["executes"][-1]
    assert "LEFT JOIN public.property_score_stat pss ON pss.property_id = p.id" in query_sql
    assert "pss.safety_score >= %s" in query_sql
    assert "ORDER BY pss.safety_score DESC NULLS LAST, p.created_at DESC" in query_sql
    assert query_params == [70, 5]
    assert rows[0]["safety_score"] == 91


def test_search_properties_does_not_join_safety_scores_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: dict[str, object] = {"executes": []}

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback) -> None:
            return None

        def execute(self, sql, params=None) -> None:
            calls["executes"].append((sql, params))

        def fetchall(self) -> list[dict]:
            return []

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback) -> None:
            return None

        def cursor(self) -> FakeCursor:
            return FakeCursor()

    monkeypatch.setattr(
        supabase_module.psycopg,
        "connect",
        lambda *args, **kwargs: FakeConnection(),
    )

    SupabaseVectorClient().search_properties({"property_type": "ONE_ROOM"}, limit=5)

    query_sql, query_params = calls["executes"][-1]
    assert "property_score_stat" not in query_sql
    assert query_params == ["ONE_ROOM", 5]


def test_property_criteria_fallback_detects_safety_sort() -> None:
    client = LLMClient(api_key="", model="")

    criteria = client.extract_property_criteria("안전점수 높은 순으로 원룸 추천해줘")

    assert criteria["sort_by"] == "safety_desc"
    assert criteria["property_type"] == "ONE_ROOM"
