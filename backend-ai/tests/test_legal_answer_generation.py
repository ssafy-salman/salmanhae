from app.clients.llm_client import LLMClient, extract_chat_completion_text
from app.graph.state import Intent
from app.rag.prompts import build_legal_rag_prompt, format_legal_context


LEGAL_CARDS = [
    {
        "lawName": "주택임대차보호법",
        "articleNo": "제3조의2",
        "title": "보증금의 회수",
        "content": "확정일자를 갖춘 임차인은 경매 또는 공매 시 보증금을 우선변제받을 수 있습니다.",
        "score": 0.91,
    },
    {
        "lawName": "전세사기피해자 지원 및 주거안정에 관한 특별법",
        "articleNo": "제1조",
        "title": "목적",
        "content": "전세사기피해자를 지원하고 주거안정을 도모하는 것을 목적으로 합니다.",
        "score": 0.82,
    },
]


def test_format_legal_context_includes_article_metadata_and_content() -> None:
    context = format_legal_context(LEGAL_CARDS)

    assert "[1] 주택임대차보호법 제3조의2 - 보증금의 회수" in context
    assert "확정일자를 갖춘 임차인" in context
    assert "[2] 전세사기피해자 지원 및 주거안정에 관한 특별법 제1조 - 목적" in context


def test_build_legal_rag_prompt_uses_question_and_context() -> None:
    prompt = build_legal_rag_prompt("보증금은 어떻게 돌려받나요?", LEGAL_CARDS)

    assert "보증금은 어떻게 돌려받나요?" in prompt
    assert "Retrieved legal references" in prompt
    assert "주택임대차보호법 제3조의2" in prompt
    assert "전문가 검토" in prompt


def test_llm_client_generates_grounded_legal_answer_from_cards() -> None:
    answer = LLMClient(api_key="").generate_answer(
        {
            "user_id": "user-1",
            "session_id": None,
            "message": "보증금은 어떻게 돌려받나요?",
            "context": {},
            "intent": Intent.LEGAL_CONSULT,
            "legal_cards": LEGAL_CARDS,
        }
    )

    assert "주택임대차보호법 제3조의2" in answer
    assert "보증금의 회수" in answer
    assert "확정일자" in answer
    assert "전문가" in answer


def test_llm_client_does_not_invent_citations_without_cards() -> None:
    answer = LLMClient(api_key="").generate_answer(
        {
            "user_id": "user-1",
            "session_id": None,
            "message": "보증금은 어떻게 돌려받나요?",
            "context": {},
            "intent": Intent.LEGAL_CONSULT,
            "legal_cards": [],
        }
    )

    assert "제3조" not in answer
    assert "검색된 법령 근거가 없습니다" in answer
    assert "전문가" in answer


def test_llm_client_uses_live_chat_completion_when_configured() -> None:
    calls = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "choices": [
                    {
                        "message": {
                            "content": "검색된 법령을 근거로 질문별 맞춤 답변을 생성했습니다."
                        }
                    }
                ]
            }

    def fake_post(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        return FakeResponse()

    answer = LLMClient(
        api_key="test-key",
        model="test-model",
        base_url="https://example.test/v1",
        http_post=fake_post,
    ).generate_answer(
        {
            "user_id": "user-1",
            "session_id": None,
            "message": "확정일자는 언제 받아야 하나요?",
            "context": {},
            "intent": Intent.LEGAL_CONSULT,
            "legal_cards": LEGAL_CARDS,
        }
    )

    assert answer == "검색된 법령을 근거로 질문별 맞춤 답변을 생성했습니다."
    assert calls[0]["args"] == ("https://example.test/v1/chat/completions",)
    assert calls[0]["kwargs"]["headers"]["Authorization"] == "Bearer test-key"
    assert calls[0]["kwargs"]["json"]["model"] == "test-model"
    assert "확정일자는 언제 받아야 하나요?" in calls[0]["kwargs"]["json"]["messages"][1]["content"]


def test_extract_chat_completion_text_supports_text_parts() -> None:
    assert (
        extract_chat_completion_text(
            {
                "choices": [
                    {
                        "message": {
                            "content": [
                                {"type": "text", "text": "첫 문장"},
                                {"type": "output_text", "text": "둘째 문장"},
                            ]
                        }
                    }
                ]
            }
        )
        == "첫 문장\n둘째 문장"
    )


def test_extract_chat_completion_text_handles_malformed_payloads() -> None:
    assert extract_chat_completion_text([]) is None
    assert extract_chat_completion_text({}) is None
    assert extract_chat_completion_text({"choices": []}) is None
    assert extract_chat_completion_text({"choices": [{"message": None}]}) is None
