#!/usr/bin/env bash
# Bash 도구 실행 전 위험한 명령어를 감지하여 차단한다.
# PreToolUse hook — Bash 도구 실행 전 작동.

set -euo pipefail

COMMAND="${COMMAND:-}"

# 위험 패턴 목록
DANGEROUS_PATTERNS=(
  "rm -rf"
  "git push --force"
  "git push -f"
  "git reset --hard"
  "git clean -f"
  "git clean -fd"
  "DROP TABLE"
  "DROP DATABASE"
  "TRUNCATE"
  "rm -r /"
  "chmod -R 777"
  "> /dev/sda"
  "mkfs"
  "dd if="
  "fork bomb"
  ":(){ :|:& };:"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qi "$pattern"; then
    echo "❌ [Dangerous Command Guard] 위험한 명령어가 감지되어 차단되었습니다." >&2
    echo "   명령어: $COMMAND" >&2
    echo "   패턴: $pattern" >&2
    echo "   이 명령이 정말 필요하다면 직접 터미널에서 실행하세요." >&2
    exit 2  # exit 2 = Claude Code가 해당 도구 실행을 차단
  fi
done

exit 0
