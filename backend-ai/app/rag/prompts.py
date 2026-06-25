LEGAL_RAG_SYSTEM_PROMPT = """\
You are the Salmanhae legal RAG assistant.
Answer only from retrieved Korean housing lease law references when possible.
Explain uncertainty clearly and recommend professional review for real contracts.
"""

GENERAL_AGENT_SYSTEM_PROMPT = """\
You are the Salmanhae real-estate safety assistant.
Use Spring Boot tool results for property, price, and safety data.
Do not invent listings or legal facts.
"""

ANALYSIS_ANSWER_SYSTEM_PROMPT = """\
You are the Salmanhae real-estate analysis assistant. Answer in Korean.
Use only the provided analysis data to answer. Mention concrete numbers when available.
Never expose internal field names (e.g. regionalStats, regionStatCount, requiresSelection, stub) or system names (e.g. Spring Boot) in your response.
Do not make HUG eligibility conclusions or legal-contract advice.
If data is insufficient, respond with a friendly Korean sentence suggesting the user try a different region or condition.
"""


def format_legal_context(legal_cards: list[dict], max_cards: int = 3) -> str:
    if not legal_cards:
        return "No retrieved legal references."

    lines: list[str] = []
    for index, card in enumerate(legal_cards[:max_cards], 1):
        law_name = card.get("lawName", "")
        article_no = card.get("articleNo", "")
        title = card.get("title", "")
        content = card.get("content", "")
        lines.append(f"[{index}] {law_name} {article_no} - {title}\n{content}")
    return "\n\n".join(lines)


def build_legal_rag_prompt(question: str, legal_cards: list[dict]) -> str:
    context = format_legal_context(legal_cards)
    return "\n\n".join(
        [
            LEGAL_RAG_SYSTEM_PROMPT.strip(),
            f"User question:\n{question.strip()}",
            f"Retrieved legal references:\n{context}",
            "Answer in Korean. Cite the law name and article number from the retrieved references. "
            "Add a short explanation and recommend 전문가 검토 for real contracts.",
        ]
    )


def build_analysis_answer_prompt(
    question: str,
    analysis_cards: list[dict],
    tool_results_json: str,
) -> str:
    return "\n\n".join(
        [
            ANALYSIS_ANSWER_SYSTEM_PROMPT.strip(),
            f"User question:\n{question.strip()}",
            f"Analysis cards:\n{analysis_cards}",
            f"Tool results:\n{tool_results_json}",
            "Answer in 2-4 concise Korean sentences. Use only grounded facts from the data above. Do not mention internal field names or system names.",
        ]
    )
