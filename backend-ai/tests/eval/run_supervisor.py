"""
supervisor 패턴의 성능 측정 스크립트.

측정 항목: 복합 의도 완전 처리율, 재현율, 응답 지연(ms), 턴당 토큰 수

실행:
    cd backend-ai
    .venv/bin/python -m tests.eval.run_supervisor

결과는 tests/eval/supervisor_result.json 에 저장된다.
baseline_result.json과 비교해 Supervisor 도입 효과를 수치화한다.

사전 조건:
    - uvicorn app.main:app 이 실행 중이어야 한다 (http://localhost:8000)
    - .env 파일에 INTERNAL_API_KEY 설정 필요
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.core.config import get_settings
from tests.eval.eval_set import EVAL_SET

BASE_URL = "http://localhost:8000"


def _invoke_supervisor(
    message: str,
    api_key: str,
    timeout: float = 60.0,
) -> tuple[list[str], float, dict[str, int]]:
    """supervisor 그래프를 한 번 호출하고 (workers_called, latency_ms, token_usage)를 반환."""
    start = time.perf_counter()
    try:
        response = httpx.post(
            f"{BASE_URL}/internal/agent/chat",
            headers={
                "X-Internal-Api-Key": api_key,
                "Content-Type": "application/json",
            },
            json={
                "userId": "eval-runner",
                "sessionId": None,
                "message": message,
                "context": {"selectedPropertyId": None, "recentMessages": []},
            },
            timeout=timeout,
        )
        latency_ms = (time.perf_counter() - start) * 1000
        response.raise_for_status()
        body = response.json()
        workers_called = body.get("workersCalled", [])
        # 토큰 수는 API 응답에 포함되지 않으므로 supervisor 호출 횟수 기반 추산
        # supervisor 1회 ≈ baseline 평균 268 토큰
        supervisor_calls = len(workers_called) + 1  # workers + FINISH 판단
        est_tokens = supervisor_calls * 268
        usage = {
            "supervisor_calls": supervisor_calls,
            "estimated_total_tokens": est_tokens,
        }
        return workers_called, latency_ms, usage
    except (httpx.HTTPError, KeyError, ValueError) as e:
        latency_ms = (time.perf_counter() - start) * 1000
        return [], latency_ms, {"supervisor_calls": 0, "estimated_total_tokens": 0}


def main() -> None:
    settings = get_settings()

    if not settings.internal_api_key:
        print("[오류] INTERNAL_API_KEY가 설정되지 않았습니다.")
        sys.exit(1)

    # 서버 살아있는지 확인
    try:
        httpx.get(f"{BASE_URL}/health", timeout=5.0).raise_for_status()
    except httpx.HTTPError:
        print(f"[오류] {BASE_URL} 에 접근할 수 없습니다. uvicorn이 실행 중인지 확인하세요.")
        sys.exit(1)

    results = []
    single_total = sum(1 for c in EVAL_SET if not c.is_complex)
    complex_total = sum(1 for c in EVAL_SET if c.is_complex)
    print(f"총 {len(EVAL_SET)}개 케이스 (단순 {single_total}개 / 복합 {complex_total}개)\n")

    for i, case in enumerate(EVAL_SET, 1):
        workers_called, latency_ms, usage = _invoke_supervisor(
            case.message, api_key=settings.internal_api_key
        )

        expected_set = set(case.expected_workers)
        got_set = set(workers_called)

        fully_correct = expected_set == got_set
        recall = len(expected_set & got_set) / len(expected_set) if expected_set else 0.0
        status = "✓" if fully_correct else "✗"

        est = usage["estimated_total_tokens"]
        calls = usage["supervisor_calls"]
        print(
            f"[{i:02d}] {status}  {case.message[:38]:<38}  "
            f"got={str(list(got_set)):<40}  {latency_ms:>6.0f}ms  "
            f"supervisor={calls}회  est_tok≈{est}"
        )

        results.append({
            "message": case.message,
            "expected_workers": case.expected_workers,
            "is_complex": case.is_complex,
            "note": case.note,
            "got_workers": workers_called,
            "fully_correct": fully_correct,
            "recall": round(recall, 3),
            "latency_ms": round(latency_ms, 1),
            "usage": usage,
        })

    # ── 요약 ──────────────────────────────────────────────────────────────────
    single_results = [r for r in results if not r["is_complex"]]
    complex_results = [r for r in results if r["is_complex"]]

    single_correct = sum(1 for r in single_results if r["fully_correct"])
    complex_fully_correct = sum(1 for r in complex_results if r["fully_correct"])
    complex_avg_recall = (
        sum(r["recall"] for r in complex_results) / len(complex_results)
        if complex_results else 0
    )
    avg_latency = sum(r["latency_ms"] for r in results) / len(results)
    avg_supervisor_calls = (
        sum(r["usage"]["supervisor_calls"] for r in results) / len(results)
    )
    avg_est_tokens = (
        sum(r["usage"]["estimated_total_tokens"] for r in results) / len(results)
    )

    summary = {
        "single_intent_total": len(single_results),
        "single_intent_correct": single_correct,
        "single_intent_accuracy": round(single_correct / len(single_results), 3) if single_results else 0,
        "complex_total": len(complex_results),
        "complex_fully_correct": complex_fully_correct,
        "complex_full_accuracy": round(complex_fully_correct / len(complex_results), 3) if complex_results else 0,
        "complex_avg_recall": round(complex_avg_recall, 3),
        "avg_latency_ms": round(avg_latency, 1),
        "avg_supervisor_calls": round(avg_supervisor_calls, 2),
        "avg_estimated_tokens_per_turn": round(avg_est_tokens, 1),
    }

    output = {
        "metadata": {
            "run_at": datetime.now(timezone.utc).isoformat(),
            "approach": "supervisor_pattern",
        },
        "summary": summary,
        "results": results,
    }

    out_path = Path(__file__).parent / "supervisor_result.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))

    print("\n" + "─" * 60)
    print(f"단순 의도 정확도       : {single_correct}/{len(single_results)}  ({summary['single_intent_accuracy']:.1%})")
    print(f"복합 의도 완전 처리율  : {complex_fully_correct}/{len(complex_results)}  ({summary['complex_full_accuracy']:.1%})")
    print(f"복합 의도 평균 재현율  : {complex_avg_recall:.1%}")
    print(f"평균 응답 지연         : {avg_latency:.0f}ms")
    print(f"평균 supervisor 호출   : {avg_supervisor_calls:.1f}회/턴")
    print(f"평균 추산 토큰         : {avg_est_tokens:.0f}  (supervisor 호출 수 × 268)")
    print(f"\n결과 저장 → {out_path}")


if __name__ == "__main__":
    main()
