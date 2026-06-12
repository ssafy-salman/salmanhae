#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== PR 생성 ===${NC}\n"

# 현재 브랜치 + 이슈 번호 추출
BRANCH=$(git branch --show-current)
ISSUE_NUMBER=$(echo "$BRANCH" | grep -o '[0-9]\+' | head -1)

if [ -z "$ISSUE_NUMBER" ]; then
  read -p "이슈 번호를 찾을 수 없습니다. 직접 입력: " ISSUE_NUMBER
fi

echo "브랜치: $BRANCH"
echo "연결 이슈: #$ISSUE_NUMBER"

# Push
echo -e "\n${BLUE}Push 중...${NC}"
git push origin "$BRANCH"

# PR 생성
echo -e "\n${BLUE}PR 생성 중...${NC}"
PR_URL=$(gh pr create \
  --title "$(git log -1 --pretty=%s)" \
  --body "## 변경 내용

## 연결 이슈
closes #$ISSUE_NUMBER

## 테스트
- [ ] 로컬 동작 확인
- [ ] API 응답 형식 명세 일치 (06_rest_api_spec.md)")

echo -e "\n${GREEN}완료!${NC}"
echo "PR: $PR_URL"
