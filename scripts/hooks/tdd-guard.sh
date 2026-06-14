#!/usr/bin/env bash
# 구현 파일 수정 시 대응 테스트가 없으면 경고를 출력한다.
# PostToolUse hook — Edit/Write 도구 실행 후 작동.

set -euo pipefail

TOOL_NAME="${TOOL_NAME:-}"
FILE_PATH="${FILE_PATH:-}"

# Edit/Write 도구가 아닌 경우 통과
if [[ "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "Write" ]]; then
  exit 0
fi

# 구현 파일 패턴 (테스트 파일 자체는 제외)
if [[ "$FILE_PATH" == *"test"* ]] || [[ "$FILE_PATH" == *"Test"* ]] || \
   [[ "$FILE_PATH" == *"spec"* ]] || [[ "$FILE_PATH" == *"Spec"* ]]; then
  exit 0
fi

# 감시 대상: Spring Boot Service, FastAPI 라우터/그래프, Vue composables
IS_SERVICE=false
if [[ "$FILE_PATH" == *"/service/"* ]] && [[ "$FILE_PATH" == *.java ]]; then
  IS_SERVICE=true
fi
if [[ "$FILE_PATH" == *"/graph/"* ]] && [[ "$FILE_PATH" == *.py ]]; then
  IS_SERVICE=true
fi
if [[ "$FILE_PATH" == *"/rag/"* ]] && [[ "$FILE_PATH" == *.py ]]; then
  IS_SERVICE=true
fi
if [[ "$FILE_PATH" == *"/composables/"* ]] && [[ "$FILE_PATH" == *.ts ]]; then
  IS_SERVICE=true
fi

if [[ "$IS_SERVICE" == "false" ]]; then
  exit 0
fi

# 대응 테스트 파일 존재 여부 확인
BASENAME=$(basename "$FILE_PATH" | sed 's/\.[^.]*$//')

# Spring Boot: Service → Test
if [[ "$FILE_PATH" == *.java ]]; then
  TEST_PATTERN="*${BASENAME}Test.java"
  FOUND=$(find . -name "$TEST_PATTERN" 2>/dev/null | head -1)
fi

# Python: module → test_module
if [[ "$FILE_PATH" == *.py ]]; then
  TEST_PATTERN="test_${BASENAME}.py"
  FOUND=$(find . -name "$TEST_PATTERN" 2>/dev/null | head -1)
fi

# Vue: composable → composable.test.ts
if [[ "$FILE_PATH" == *.ts ]]; then
  TEST_PATTERN="${BASENAME}.test.ts"
  FOUND=$(find . -name "$TEST_PATTERN" 2>/dev/null | head -1)
fi

if [[ -z "${FOUND:-}" ]]; then
  echo "⚠️  [TDD Guard] '$FILE_PATH' 수정됨 — 대응 테스트 파일을 찾을 수 없습니다." >&2
  echo "   CLAUDE.md CRITICAL: 새 기능 구현 시 테스트를 먼저 작성하세요." >&2
  # 경고만 출력 (차단하지 않음 — exit 1로 바꾸면 강제 차단)
fi

exit 0
