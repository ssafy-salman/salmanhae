#!/usr/bin/env bash
# 같은 에러가 60초 내에 5번 반복되면 전략 변경을 경고한다.
# PostToolUse hook — 도구 실행 후 에러 감지 시 작동.

set -euo pipefail

TOOL_NAME="${TOOL_NAME:-}"
EXIT_CODE="${EXIT_CODE:-0}"
OUTPUT="${OUTPUT:-}"

# 에러가 아닌 경우 통과
if [[ "$EXIT_CODE" == "0" ]]; then
  exit 0
fi

STATE_DIR="/tmp/salmanhae-circuit-breaker"
mkdir -p "$STATE_DIR"

# 에러 내용 해시 (처음 200자 기준)
ERROR_HASH=$(echo "${OUTPUT:0:200}" | md5sum | cut -d' ' -f1)
STATE_FILE="$STATE_DIR/$ERROR_HASH"

NOW=$(date +%s)
WINDOW=60    # 60초 윈도우
THRESHOLD=5  # 5회 반복 시 경고

# 기존 타임스탬프 로드 및 윈도우 밖 항목 제거
TIMESTAMPS=()
if [[ -f "$STATE_FILE" ]]; then
  while IFS= read -r ts; do
    if (( NOW - ts <= WINDOW )); then
      TIMESTAMPS+=("$ts")
    fi
  done < "$STATE_FILE"
fi

# 현재 타임스탬프 추가
TIMESTAMPS+=("$NOW")

# 상태 파일 업데이트
printf '%s\n' "${TIMESTAMPS[@]}" > "$STATE_FILE"

COUNT="${#TIMESTAMPS[@]}"

if (( COUNT >= THRESHOLD )); then
  echo "" >&2
  echo "🔴 [Circuit Breaker] 동일한 에러가 ${WINDOW}초 내 ${COUNT}회 반복되었습니다." >&2
  echo "   에러 패턴: ${OUTPUT:0:100}..." >&2
  echo "" >&2
  echo "   현재 전략이 효과적이지 않습니다. 다음을 고려하세요:" >&2
  echo "   1. 문제의 근본 원인을 먼저 진단하세요." >&2
  echo "   2. 다른 접근 방식을 시도하세요." >&2
  echo "   3. docs/ 문서에서 관련 ADR·아키텍처 제약을 재확인하세요." >&2
  echo "" >&2
fi

exit 0
