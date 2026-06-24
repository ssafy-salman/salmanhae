"""
단일 intent LLM 분류 방식의 베이스라인 측정 스크립트.

측정 항목: 정확도, 응답 지연(ms), 턴당 토큰 수(prompt / completion / total)

실행:
    cd backend-ai
    .venv/bin/python -m tests.eval.run_baseline

결과는 tests/eval/baseline_result.json 에 저장된다.
supervisor 패턴 도입 후 tests/eval/run_supervisor.py로 재측정해 비교한다.

사전 조건:
    - .env 파일에 GMS_API_KEY, LLM_BASE_URL, LLM_MODEL 설정 필요
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from pydantic import ValidationError

from app.clients.llm_client import CLASSIFY_INTENT_PROMPT, extract_chat_completion_text
from app.core.config import get_settings
from app.graph.nodes.classify_intent import RouteDecision
from app.graph.state import Intent
from tests.eval.eval_set import EVAL_SET


def _classify_with_usage(
    message: str,
    base_url: str,
    api_key: str,
    model: str,
    timeout: float = 20.0,
) -> tuple[Intent, dict[str, int]]:
    """classify_intent_llm과 동일한 로직이지만 token usage도 함께 반환한다."""
    prompt = CLASSIFY_INTENT_PROMPT.format(message=message)
    usage: dict[str, int] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    try:
        response = httpx.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_completion_tokens": 128,
            },
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()

        raw_usage = payload.get("usage", {})
        usage = {
            "prompt_tokens": raw_usage.get("prompt_tokens", 0),
            "completion_tokens": raw_usage.get("completion_tokens", 0),
            "total_tokens": raw_usage.get("total_tokens", 0),
        }

        text = extract_chat_completion_text(payload) or "{}"
        parsed = json.loads(text)
        decision = RouteDecision.model_validate(parsed)
        return Intent(decision.intent), usage

    except (httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError, ValueError, ValidationError):
        return Intent.FALLBACK, usage


def main() -> None:
    settings = get_settings()

    if not settings.gms_api_key or not settings.llm_model or not settings.llm_base_url:
        print("[오류] GMS_API_KEY, LLM_BASE_URL, LLM_MODEL 중 미설정 항목이 있습니다.")
        print("       .env 파일을 확인하세요.")
        sys.exit(1)

    base_url = settings.llm_base_url.rstrip("/")
    results = []

    single_total = sum(1 for c in EVAL_SET if not c.is_complex)
    complex_total = sum(1 for c in EVAL_SET if c.is_complex)
    print(f"총 {len(EVAL_SET)}개 케이스 (단순 {single_total}개 / 복합 {complex_total}개)\n")

    for i, case in enumerate(EVAL_SET, 1):
        start = time.perf_counter()
        got, usage = _classify_with_usage(
            case.message,
            base_url=base_url,
            api_key=settings.gms_api_key,
            model=settings.llm_model,
        )
        latency_ms = (time.perf_counter() - start) * 1000

        got_str = got.value if hasattr(got, "value") else str(got)
        got_set = {got_str}
        expected_set = set(case.expected_workers)

        if case.is_complex:
            fully_correct = False  # 단일 intent 구조는 복합 의도를 완전 처리 불가
            recall = len(expected_set & got_set) / len(expected_set)
            status = "✗"
        else:
            fully_correct = got_str == case.expected_workers[0]
            recall = 1.0 if fully_correct else 0.0
            status = "✓" if fully_correct else "✗"

        tokens_str = f"tok={usage['total_tokens']}" if usage["total_tokens"] else "tok=?"
        print(
            f"[{i:02d}] {status}  {case.message[:38]:<38}  "
            f"got={got_str:<20}  {latency_ms:>6.0f}ms  {tokens_str}"
        )

        results.append({
            "message": case.message,
            "expected_workers": case.expected_workers,
            "is_complex": case.is_complex,
            "note": case.note,
            "got_intent": got_str,
            "fully_correct": fully_correct,
            "recall": round(recall, 3),
            "latency_ms": round(latency_ms, 1),
            "tokens": usage,
        })

    # ── 요약 계산 ──────────────────────────────────────────────────────────────
    single_results = [r for r in results if not r["is_complex"]]
    complex_results = [r for r in results if r["is_complex"]]

    single_correct = sum(1 for r in single_results if r["fully_correct"])
    complex_fully_correct = 0  # 단일 intent 구조상 항상 0
    complex_avg_recall = (
        sum(r["recall"] for r in complex_results) / len(complex_results)
        if complex_results else 0
    )

    avg_latency = sum(r["latency_ms"] for r in results) / len(results)

    all_tokens = [r["tokens"]["total_tokens"] for r in results if r["tokens"]["total_tokens"] > 0]
    avg_tokens = sum(all_tokens) / len(all_tokens) if all_tokens else 0
    avg_prompt_tokens = (
        sum(r["tokens"]["prompt_tokens"] for r in results if r["tokens"]["prompt_tokens"] > 0)
        / len(all_tokens) if all_tokens else 0
    )
    avg_completion_tokens = (
        sum(r["tokens"]["completion_tokens"] for r in results if r["tokens"]["completion_tokens"] > 0)
        / len(all_tokens) if all_tokens else 0
    )

    summary = {
        "single_intent_total": len(single_results),
        "single_intent_correct": single_correct,
        "single_intent_accuracy": round(single_correct / len(single_results), 3) if single_results else 0,
        "complex_total": len(complex_results),
        "complex_fully_correct": complex_fully_correct,
        "complex_full_accuracy": 0.0,
        "complex_avg_recall": round(complex_avg_recall, 3),
        "avg_latency_ms": round(avg_latency, 1),
        "avg_tokens_per_turn": round(avg_tokens, 1),
        "avg_prompt_tokens": round(avg_prompt_tokens, 1),
        "avg_completion_tokens": round(avg_completion_tokens, 1),
    }

    output = {
        "metadata": {
            "run_at": datetime.now(timezone.utc).isoformat(),
            "approach": "single_intent_llm",
            "model": settings.llm_model,
        },
        "summary": summary,
        "results": results,
    }

    out_path = Path(__file__).parent / "baseline_result.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))

    print("\n" + "─" * 60)
    print(f"단순 의도 정확도       : {single_correct}/{len(single_results)}  ({summary['single_intent_accuracy']:.1%})")
    print(f"복합 의도 완전 처리율  : {complex_fully_correct}/{len(complex_results)}  (0.0%)  ← 구조적 한계")
    print(f"복합 의도 평균 재현율  : {complex_avg_recall:.1%}  (참고)")
    print(f"평균 응답 지연         : {avg_latency:.0f}ms")
    print(f"평균 턴당 토큰         : {avg_tokens:.0f}  (prompt {avg_prompt_tokens:.0f} / completion {avg_completion_tokens:.0f})")
    print(f"\n결과 저장 → {out_path}")
    print("\n[참고] 복합 완전 처리 = 필요한 워커 전부 호출 (단일 intent 구조상 항상 0%)")
    print("       supervisor 도입 후 run_supervisor.py로 재측정해 비교하세요.")


if __name__ == "__main__":
    main()
